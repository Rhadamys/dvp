<template>
    <div class="container md-layout md-gutter">
        <div class="md-layout-item md-size-50 md-small-size-100">
            <md-card class="md-primary md-elevation-6 editor">
                <div class="editor-code-running" v-if="running.active" @click="running.dialog = true"></div>
                <editor-toolbar :exceptions="exceptions" :stepping="stepping"></editor-toolbar>
                <editor></editor>
                <conditional id="editor-conditional"></conditional>
                <md-button class="md-raised editor-limit-reached"
                    @click="exceptions.limit.dialog = true"
                    v-if="exceptions.limit.reached">
                    <md-icon>error</md-icon>&ensp;Límite alcanzado
                </md-button>
                <md-dialog :md-active.sync="exceptions.limit.dialog">
                    <md-dialog-title class="md-dialog-danger">
                        LÍMITE DE EJECUCIÓN ALCANZADO
                    </md-dialog-title>
                    <md-dialog-content v-html="exceptions.limit.message"></md-dialog-content>
                    <md-dialog-actions>
                        <md-button class="md-primary" @click="exceptions.limit.dialog = false">Cerrar</md-button>
                    </md-dialog-actions>
                </md-dialog>
            </md-card>
        </div>
        <div class="md-layout-item md-size-50 md-small-size-100 visual-panel">
            <console class="md-elevation-6" 
                :hide="expanded.trace" 
                :expanded="expanded.console"
                @resize="expanded.console = !expanded.console"></console>
            <trace class="md-elevation-6" 
                :hide="expanded.console" 
                :expanded="expanded.trace" 
                :step="stepping.current"
                @resize="expanded.trace = !expanded.trace"></trace>
        </div>
        <md-snackbar md-position="left" :md-duration="Infinity" :md-active.sync="running.active" md-theme="default-light">
            <md-progress-spinner class="md-accent" :md-diameter="30" :md-value="timeout.perc" :md-mode="timeout.time > 0 ? 'determinate' : 'indeterminate'"></md-progress-spinner>
            <span>Ejecutando código...</span>
        </md-snackbar>
        <md-dialog-alert
            :md-active.sync="running.dialog"
            md-title="Tu código aún se está ejecutando..."
            :md-content="'Por favor, espera hasta que termine para realizar alguna acción en el editor. ' + (timeout.time > 0 ? 'La ejecución se detendrá automáticamente dentro de <u>' + timeout.time / 1000 + ' segundos</u>.' : '<u>Esperando respuesta del servidor...</u>')" />
        </div>
</template>
<script>
import Annotations from '@/annotations'
import Const from '@/const'
import Events from '@/events'
import Parser from '@/parser'
import Conditional from '../components/conditional/Conditional'
import Editor from '../components/editor/Editor'
import IOConsole from '../components/Console'
import Toolbar from '../components/editor/Toolbar'
import Trace from '../components/trace/Trace'

export default {
    data: function() {
        return {
            /**
             * Excepciones encontradas en la ejecución. Se actualiza cada vez que se
             * envía código al servidor.
             */
            exceptions: {
                errors: [],
                limit: {
                    reached: false,
                    message: '',
                    dialog: false,
                },
                /**
                 * Al recibir respuesta del servidor es "true" para buscar errores y advertencias
                 * en la ejecución. Luego es "false" para mentenerlos hasta la siguiente ejecución.
                 */
                searching: true,
                warnings: [],
            },
            expanded: {
                console: false,
                trace: false,
            },
            parsed: {
                conditional: {},
                stack: {},
            },
            running: {
                active: false,
                dialog: false,
            },
            stepping: {
                current: undefined,
                last: undefined,
            },
            timeout: {
                interval: undefined,
                perc: undefined,
                step: 100,
                time: undefined,
            },
            /**
             * Traza de ejecución devuelta desde el servidor.
             */
            trace: undefined,
        }
    },
    components: {
        'conditional': Conditional,
        'console': IOConsole,
        'editor': Editor,
        'editor-toolbar': Toolbar,
        'trace': Trace,
    },
    created: function() {
        this.$root.$on(Events.REQUEST_STEPPING, () => { this.$root.$emit(Events.UPDATE_STEPPING, this.stepping) })
        this.$root.$on(Events.SEND_INPUT, this.send)
        this.$root.$on(Events.SEND_SCRIPT, this.send)
        this.$root.$on(Events.SET_STEP, (step) => {
            this.stepping.current = step
            this.render(step)
        })
    },
    methods: {
        /**
         * Envía el código al servidor para generar la traza de ejecución.
         * @param addPayload Data adicional para enviar al servidor.
         */
        send: function(addPayload = {}) {
            const script = localStorage.getItem('script')
            this.exceptions.limit.reached = false

            this.$http
                .post('/trace', { ...addPayload, script })
                .then(response => {
                    this.response(response.data)
                })
                .catch(e => {
                    this.running.active = false
                    this.$root.$emit(Events.SHOW_SNACK, { 
                        className: 'card-danger', 
                        duration: 5000,
                        message: Const.ERR_CONNECTION,
                    })
                })

            this.running.active = true
            this.startTimeout()
        },
        startTimeout: function() {
            this.timeout.time = Const.MAX_TIME_RUNNING  
            this.timeout.perc = 100
            clearInterval(this.timeout.interval)
            this.timeout.interval = setInterval(() => {
                this.timeout.time -= this.timeout.step
                this.timeout.perc = this.timeout.time * 100 / Const.MAX_TIME_RUNNING

                if(this.timeout.perc > 0) return
                clearInterval(this.timeout.interval)
            }, this.timeout.step)
        },
        /**
         * Se ejecuta al recibir respuesta del servidor luego de haber enviado código
         * para su ejecución.
         * @param data Respuesta del servidor.
         */
        response: function(data) {
            this.parsed = { conditional: {}, stack: {} }
            this.trace = data
            
            // Elimina las excepciones de la ejecución anterior
            this.exceptions.errors = []
            this.exceptions.warnings = []
            this.exceptions.searching = true // Indica que deben anotarse las excepciones

            const last = this.trace.length - 1
            this.stepping.current = this.stepping.last = last
            this.render(last)

            this.$root.$emit(Events.UPDATE_STEPPING, this.stepping)
        },
        /**
         * Renderiza los elementos de traza en el editor
         * @param current Paso actual
         */
        render: function(current) {
            this.$root.$emit(Events.CLEAR_HIGHLIGHT)
            const steps = this.trace.slice(0, current + 1)
            steps.forEach(this.renderStep)
            
            // Indica que no deben anotarse nuevas excepciones hasta la próxima ejecución
            this.exceptions.searching = false
        },
        /**
         * Renderiza los elementos gráficos del editor para el paso actual. También agrega marcadores
         * (indicadores de color y mensajes) si corresponde.
         * @param step Paso de ejecución actual
         * @param index Número de paso de ejecución
         */
        renderStep: function(step, index) {
            if(this.exceptions.searching) {
                if(step.stack_to_render)
                    this.parsed.stack[index] = new Promise(function(resolve, reject) { resolve(Parser.parseStack(step.stack_to_render)) })
                if(step.conditional || (step.loop && step.loop.conditional)) {
                    const cond = step.conditional || step.loop.conditional
                    this.parsed.conditional[index] = new Promise(function(resolve, reject) { resolve(Parser.parseConditional(cond)) })
                }
            }

            if(step.event === Const.EVENT_LIMIT_REACHED) { // Límite de pasos
                this.renderLimitReached(step, index - 1)
                return
            } else if(step.event === Const.EVENT_RAW_INPUT) { // Input
                this.renderPrompt(step, this.trace[index - 1])
                this.finishRender(step, index)
                return
            } else if(step.event === Const.EVENT_EXCEPTION && index < this.stepping.last) { // Excepción controlada
                this.renderException(step, index)
            } else if(step.event.includes(Const.EVENT_EXCEPTION)) { // Excepción al final
                this.renderUncaughtException(step, index)
                return
            }
            
            if(index === this.stepping.current) { // Si es el paso actual en la ejecución paso a paso
                const next = this.trace[index + 1]
                this.renderLastStep(step, next, index)
                this.$root.$emit(Events.CLEAR_INPUT)
                this.finishRender(step, index)
            } 
        },
        /**
         * Renderiza el último paso de la ejecución, en el cual se indica la línea de
         * ejecución actual y la línea de ejecución siguiente.
         * @param current Paso de ejecución actual
         * @param next Paso de ejecución siguiente
         */
        renderLastStep: function(current, next) {
            const current_row = current.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: current_row, 
                column: 0, 
                text: 'Línea actual', 
                type: Annotations.CURRENT_LINE
            })
            
            if(next === undefined) return
            const next_row = next.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: next_row, 
                column: 0, 
                text: 'Línea siguiente', 
                type: Annotations.NEXT_LINE
            })
        },
        /**
         * Indica cuando se ha alcanzado el límite de pasos ejecutados. Muestra un mensaje
         * en la consola.
         * @param step Paso actual donde se produjo la excepción
         * @param last_index Número del paso anterior
         */
        renderLimitReached: function(step, last_index) {
            this.exceptions.limit.message = step.exception_msg
            this.exceptions.limit.reached = true
            this.finishRender(last_index < 0 ? step : this.trace[last_index], last_index)

            // Si el límite se alcanzo por número de pasos ejecutado
            if(step.limit === Const.LIMIT_REACHED_BY_STEPS)
                this.renderLastStep(step, undefined, last_index)
                return

            // Si el límite se alcanzó por tiempo de ejecución
            this.$root.$emit(Events.HIGHLIGHT, {
                row: 0,
                column: 0,
                text: Const.LIMIT_REACHED_BY_TIME,
                type: Annotations.ERROR
            })
            
        },
        /**
         * Renderiza los elementos propios de una excepción controlada.
         * @param exception Excepción producida
         * @param index Paso en que se produjo esta excepción
         */
        renderException: function(exception, index) {
            const row = exception.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: row,
                column: exception.offset, 
                text: exception.exception_msg, 
                type: Annotations.WARNING
            })

            if(!this.exceptions.searching) return
            this.exceptions.warnings.push({
                step: index,
                lineno: exception.line,
                message: exception.exception_msg
            })
        },
        /**
         * Renderiza los elementos propios de una excepción no controlada (abortar ejecución).
         * @param exception Excepción producida
         * @param index Paso en que se produjo esta excepción
         */
        renderUncaughtException: function(exception, index) {
            const row = exception.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: row,
                column: exception.offset,
                text: exception.exception_msg,
                type: Annotations.ERROR
            })
            this.finishRender(exception, index)

            if(!this.exceptions.searching) return
            this.exceptions.errors.push({
                step: index,
                lineno: exception.line,
                message: exception.exception_msg
            })
        },
        /**
         * Renderiza los elementos propios de una solicitud de ingreso de datos por pantalla.
         * @param raw_input Objeto JSON que indica, entre otras cosas, el mensaje del "input"
         * @param last_step Número del paso anterior en la ejecución
         */
        renderPrompt: function(raw_input, last_step) {
            this.$root.$emit(Events.PROMPT_INPUT, raw_input)
            const row = last_step.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: row, 
                column: 0, 
                text: Const.PROMPT, 
                type: Annotations.PROMPT
            })
        },
        /**
         * Renderiza los últimos elementos.
         * @param step Paso actual
         */
        finishRender: function(step, index) {
            this.running.active = false
            this.running.dialog = false

            if(index in this.parsed.stack)
                this.parsed.stack[index].then(stack => this.$root.$emit(Events.SET_TRACE, stack))

            if(index in this.parsed.conditional)
                this.parsed.conditional[index].then(cond => this.$root.$emit(Events.SET_CONDITIONAL, cond))
            else
                this.$root.$emit(Events.SET_CONDITIONAL, undefined)
            
            if(!(step.event === 'return' && this.stepping.current === this.stepping.last))
                this.$root.$emit(Events.SCROLL_EDITOR, step.line)

            if(step.stdout === undefined) return
            this.$root.$emit(Events.UPDATE_CONSOLE, step.stdout)
        }
    }
}
</script>
