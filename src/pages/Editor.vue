<template>
    <div class="container md-layout md-gutter">
        <div class="md-layout-item md-size-60 md-small-size-100">
            <md-card class="md-primary md-elevation-6 editor" md-theme="secondary">
                <editor-toolbar :exceptions="exceptions" :stepping="stepping"></editor-toolbar>
                <md-progress-bar class="md-accent" md-mode="indeterminate" v-if="running"></md-progress-bar>
                <editor></editor>
                <md-button class="md-fab md-mini editor-limit-reached"
                    @click="exceptions.limit.dialog = true"
                    v-if="exceptions.limit.reached">
                    <md-icon>error</md-icon>
                    <md-tooltip md-direction="left">Límite de ejecución alcanzado</md-tooltip>
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
        <div class="md-layout-item md-layout-item md-size-40  md-small-size-100 visual-panel">
            <console class="md-elevation-6"></console>
            <trace v-if="!running" class="md-elevation-6" :stack="stack"></trace>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/editor.scss"></style>
<script>
import AnnotationTypes from '@/annotations'
import Const from '@/const'
import Events from '@/events'
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
            running: true,
            stack: undefined,
            stepping: {
                current: undefined,
                last: undefined,
            },
            /**
             * Traza de ejecución devuelta desde el servidor.
             */
            trace: undefined,
        }
    },
    components: {
        'console': IOConsole,
        'editor': Editor,
        'editor-toolbar': Toolbar,
        'trace': Trace,
    },
    created: function() {
        this.$root.$on(Events.REQUEST_STEPPING, () => {
            this.$root.$emit(Events.UPDATE_STEPPING, this.stepping)
        })
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
            this.running = true
            const script = localStorage.getItem('script')
            const payload = Object.assign({}, { script }, addPayload)
            this.$http
                .post(process.env.ROOT_API + 'trace/', payload)
                .then(response => {
                    this.response(response.data)
                })
        },
        /**
         * Se ejecuta al recibir respuesta del servidor luego de haber enviado código
         * para su ejecución.
         * @param data Respuesta del servidor.
         */
        response: function(data) {
            this.trace = data.trace
            
            // Elimina las excepciones de la ejecución anterior
            this.exceptions.errors = []
            this.exceptions.warnings = []
            this.exceptions.searching = true // Indica que deben anotarse las excepciones
            this.exceptions.limit.reached = false

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
            if(step.event === Const.EVENT_LIMIT_REACHED) { // Límite de pasos
                this.renderLimitReached(step, index - 1)
                return
            } else if(step.event === Const.EVENT_RAW_INPUT) { // Input
                this.renderPrompt(step, this.trace[index - 1], step)
                return
            } else if(step.event === Const.EVENT_EXCEPTION && index < this.stepping.last) { // Excepción controlada
                this.renderException(step, index)
            } else if(step.event.includes('exception')) { // Excepción al final
                this.renderUncaughtException(step, index)
                return
            }
            
            if(index === this.stepping.current) { // Si es el paso actual en la ejecución paso a paso
                const next = this.trace[index + 1]
                this.renderLastStep(step, next, index)
                this.$root.$emit(Events.CLEAR_INPUT)
                this.finishRender(step)
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
                type: AnnotationTypes.CURRENT_LINE
            })
            
            if(next === undefined) return
            const next_row = next.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: next_row, 
                column: 0, 
                text: 'Línea siguiente', 
                type: AnnotationTypes.NEXT_LINE
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
            const last_step = this.trace[last_index]
            this.renderLastStep(last_step, step, last_index)
            this.finishRender(last_step)
            this.exceptions.limit.reached = true
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
                type: AnnotationTypes.WARNING
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
                type: AnnotationTypes.ERROR
            })
            this.finishRender(exception)

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
         * @param step Paso actual en la ejecución
         */
        renderPrompt: function(raw_input, last_step, step) {
            this.$root.$emit(Events.PROMPT_INPUT, raw_input)
            const row = last_step.line - 1
            this.$root.$emit(Events.HIGHLIGHT, {
                row: row, 
                column: 0, 
                text: Const.PROMPT, 
                type: AnnotationTypes.PROMPT
            })
            this.finishRender(step)
        },
        /**
         * Renderiza los últimos elementos.
         * @param step Paso actual
         */
        finishRender: function(step) {
            this.running = false
            this.$root.$emit(Events.SCROLL_EDITOR, step.line)
            this.stack = this.trace[this.stepping.current].stack_to_render

            if(step.stdout === undefined) return
            this.$root.$emit(Events.UPDATE_CONSOLE, step.stdout)
        }
    }
}
</script>
