<template>
    <md-card class="md-primary" md-theme="secondary">
        <md-card-actions md-alignment="space-between">
            <div class="editor-exc">
                <md-button class="editor-exc-errors" @click="exceptions.dialog = !exceptions.dialog"
                    v-bind:disabled="exceptions.errors.length === 0">
                    <md-icon>error</md-icon>&ensp;{{ exceptions.errors.length }}
                    <md-tooltip md-direction="top">Errores</md-tooltip>
                </md-button>
                <md-button class="editor-exc-warnings" @click="exceptions.dialog = !exceptions.dialog"
                    v-bind:disabled="exceptions.warnings.length === 0">
                    <md-icon>warning</md-icon>&ensp;{{ exceptions.warnings.length }}
                    <md-tooltip md-direction="top">Advertencias</md-tooltip>
                </md-button>
            </div>
            <div class="editor-actions" v-if="trace && trace.length > 1">
                <md-button class="md-icon-button md-dense"
                    @click="stepping.current -= 1"
                    v-bind:disabled="stepping.current === 0">
                    <md-icon>navigate_before</md-icon>
                    <md-tooltip md-direction="top">Retroceder</md-tooltip>
                </md-button>
                <md-button class="md-icon-button md-dense"
                    @click="stepping.current += 1"
                    v-bind:disabled="stepping.current === stepping.last">
                    <md-icon>navigate_next</md-icon>
                    <md-tooltip md-direction="top">Avanzar</md-tooltip>
                </md-button>
                <md-button class="md-icon-button md-dense"
                    @click="refresh">
                    <md-icon>refresh</md-icon>
                    <md-tooltip md-direction="top">Volver a ejecutar</md-tooltip>
                </md-button>
            </div>
        </md-card-actions>
        <md-progress-bar class="md-accent" md-mode="indeterminate" v-if="ace.running"></md-progress-bar>
        <div id="ace-editor"></div>
        <md-button class="md-fab md-mini editor-limit-reached"
            @click="exceptions.limit.dialog = true"
            v-if="exceptions.limit.reached">
            <md-icon>error</md-icon>
            <md-tooltip md-direction="left">Límite de ejecución alcanzado</md-tooltip>
        </md-button>
        <md-dialog :md-active.sync="exceptions.dialog">
            <md-card class="card card-error" md-theme="default-light">
                <md-card-header>
                    <span class="md-title">
                        <md-icon>error</md-icon>&ensp;Errores
                    </span>
                </md-card-header>
                <md-table v-model="exceptions.errors" md-sort="step" md-sort-order="asc"
                    v-if="exceptions.errors.length > 0"
                    @md-selected="gotoStep" md-card>
                    <md-table-row slot="md-table-row" slot-scope="{ item }" md-selectable="single">
                        <md-table-cell md-label="Paso" md-sort-by="step" md-numeric>{{ item.step }}</md-table-cell>
                        <md-table-cell md-label="Línea" md-sort-by="lineno" md-numeric>{{ item.lineno }}</md-table-cell>
                        <md-table-cell md-label="Descripción" md-sort-by="message">{{ item.message }}</md-table-cell>
                    </md-table-row>
                </md-table>
                <p class="text-center" v-else>No se ha encontrado errores</p>
            </md-card>
            <md-card class="card card-warning" md-theme="default-light">
                <md-card-header>
                    <span class="md-title">
                        <md-icon>warning</md-icon>&ensp;Advertencias
                    </span>
                </md-card-header>
                <md-table v-model="exceptions.warnings" md-sort="step" md-sort-order="asc"
                    v-if="exceptions.warnings.length > 0"
                    @md-selected="gotoStep" md-card>
                    <md-table-row slot="md-table-row" slot-scope="{ item }" md-selectable="single">
                        <md-table-cell md-label="Paso" md-sort-by="step" md-numeric>{{ item.step }}</md-table-cell>
                        <md-table-cell md-label="Línea" md-sort-by="lineno" md-numeric>{{ item.lineno }}</md-table-cell>
                        <md-table-cell md-label="Descripción" md-sort-by="message">{{ item.message }}</md-table-cell>
                    </md-table-row>
                </md-table>
                <p class="text-center" v-else>No se ha encontrado advertencias</p>
            </md-card>
            <md-dialog-actions>
                <md-button class="md-primary" @click="exceptions.dialog = false">Cerrar</md-button>
            </md-dialog-actions>
        </md-dialog>
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
</template>
<style lang="scss" src="@/assets/styles/editor.scss"></style>
<style lang="scss" src="@/assets/styles/ace.scss"></style>
<script>
import AnnonationTypes from '@/annotations'
import Const from '@/const'
import Events from '@/events'

export default {
    data: function() {
        return {
            /**
             * Traza de ejecución devuelta desde el servidor.
             */
            trace: undefined,
            /**
             * Código actual en formato lista. Los elementos son cada una de las líneas del
             * código en el editor.
             */
            script: [],
            ace: {
                editor: {},
                markers: [],
                running: true,
            },
            stepping: {
                current: undefined,
                last: undefined,
            },
            /**
             * Timer para enviar código automáticamente al servidor luego de cumplirse
             * un breve periodo de tiempo sin realizar modificaciones en el editor, es
             * decir, cuando el usuario deja de escribir.
             */
            codeChangeTimeOut: null,
            /**
             * Excepciones encontradas en la ejecución. Se actualiza cada vez que se
             * envía código al servidor.
             */
            exceptions: {
                errors: [],
                warnings: [],
                limit: {
                    reached: false,
                    message: '',
                    dialog: false,
                },
                /**
                 * Toggle para ver / ocultar el diálogo en que se muestran los errores y
                 * excepciones encontradas.
                 */
                dialog: false,
                /**
                 * Al recibir respuesta del servidor es "true" para buscar errores y advertencias
                 * en la ejecución. Luego es "false" para mentenerlos hasta la siguiente ejecución.
                 */
                searching: true,
            },
        }
    },
    created: function() {
        this.$root.$on(Events.SEND_INPUT, this.send)
        this.$root.$on(Events.SET_STEP, (step) => {
            this.stepping.current = step
            this.render(step)
        })
    },
    mounted: function() {
        this.ace.editor = ace.edit('ace-editor')
        this.ace.editor.session.setMode('ace/mode/python')
        this.ace.editor.session.on('change', this.change)
        this.ace.editor.session.setValue(localStorage.getItem("script"))
        this.ace.editor.renderer.setScrollMargin(10, 10, 10, 10)
    },
    methods: {
        /**
         * Callback para "onChange" de Ace Editor.
         */
        change: function(delta) {
            this.$root.$emit(Events.RESET)
            localStorage.setItem('script', this.ace.editor.session.getValue())
            clearTimeout(this.codeChangeTimeOut)
            this.codeChangeTimeOut = setTimeout(() => {
                this.reset()
                this.send()
            }, 1000)
        },
        /**
         * Envía el código al servidor para generar la traza de ejecución.
         * @param addPayload Data adicional para enviar al servidor.
         */
        send: function(addPayload = {}) {
            this.ace.running = true
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
            this.ace.running = false
            this.script = data.script_lines
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
            this.reset()
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
            this.highlight(current_row, 0, 'Línea actual', AnnonationTypes.CURRENT_LINE)
            
            if(next === undefined) return
            const next_row = next.line - 1
            this.highlight(next_row, 0, 'Línea siguiente', AnnonationTypes.NEXT_LINE)
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
            this.highlight(row, exception.offset, exception.exception_msg, AnnonationTypes.WARNING)

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
            this.highlight(row, exception.offset, exception.exception_msg, AnnonationTypes.ERROR)
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
            this.highlight(row, 0, Const.PROMPT, AnnonationTypes.PROMPT)
            this.finishRender(step)
        },
        /**
         * Renderiza los últimos elementos.
         * @param step Paso actual
         */
        finishRender: function(step) {
            this.ace.editor.scrollToLine(step.line, true, true)

            if(step.stdout === undefined) return
            this.$root.$emit(Events.UPDATE_CONSOLE, step.stdout)
        },
        /**
         * Resalta una línea en el editor con un mensaje.
         * @param row Línea del código
         * @param column Columna del código
         * @param text Texto del mensaje
         * @param type Tipo de mensaje
         */
        highlight: function(row, column, text, type) {
            const annotations = this.ace.editor.getSession().getAnnotations()
            this.ace.editor.getSession().setAnnotations([...annotations, { row, column, text, type }])
            const Range = ace.require('ace/range').Range
            const marker_id = this.ace.editor.session.addMarker(new Range(row, 0, row, 1), type, 'fullLine')
            this.ace.markers.push(marker_id)
        },
        /**
         * Al seleccionar una excepción desde el diálogo de excepciones, la ejecución
         * se mueve al paso donde se produjo.
         * @param exception Excepción seleccionada en la lista
         */
        gotoStep: function(exception) {
            this.exceptions.dialog = false
            this.stepping.current = exception.step
        },
        /**
         * Vuelve a ejecutar el código. Esto es útil cuando se han ingresado datos, de esta
         * forma los volverá a solicitar.
         */
        refresh: function() {
            this.$root.$emit(Events.RESET)
            this.reset()
            this.send()
        },
        reset: function() {
            this.ace.editor.getSession().setAnnotations([])
            this.ace.markers.map(marker => {
                this.ace.editor.session.removeMarker(marker)
            })
            this.ace.markers = []
        },
    }
}
</script>
