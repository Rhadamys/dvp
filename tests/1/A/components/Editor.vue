<template>
    <md-card class="md-primary" md-theme="secondary">
        <md-card-actions md-alignment="space-between">
            <div>
                <span class="md-title">Editor</span>
            </div>
            <div class="debugger-actions" v-if="trace && trace.length > 1">
                <md-button class="md-icon-button md-dense"
                    v-on:click="step -= 1"
                    v-bind:disabled="step === 0">
                    <md-icon>navigate_before</md-icon>
                    <md-tooltip md-direction="top">Retroceder</md-tooltip>
                </md-button>
                <md-button class="md-icon-button md-dense"
                    v-if="stepping.active"
                    v-on:click="pause">
                    <md-icon class="pause-btn">pause</md-icon>
                    <md-tooltip md-direction="top">Pausar</md-tooltip>
                </md-button>
                <md-button class="md-icon-button md-dense"
                    v-on:click="play"
                    v-else >
                    <md-icon class="play-btn">play_arrow</md-icon>
                    <md-tooltip md-direction="top">Depurar</md-tooltip>
                </md-button>
                <md-button class="md-icon-button md-dense"
                    v-on:click="step += 1"
                    v-bind:disabled="step === last">
                    <md-icon>navigate_next</md-icon>
                    <md-tooltip md-direction="top">Avanzar</md-tooltip>
                </md-button>
                <md-button class="md-icon-button md-dense"
                    v-on:click="refresh">
                    <md-icon>refresh</md-icon>
                    <md-tooltip md-direction="top">Volver a ejecutar</md-tooltip>
                </md-button>
            </div>
        </md-card-actions>
        <div class="stepper" v-if="trace && trace.length > 1">
            <div v-for="(step, idx) in trace" :key="idx"
                v-bind:class="[
                    idx === 0 ? 'step first' : idx === last ? 'step last' : 'step',
                    step.event === 'raw_input' ? 'prompt' :
                    step.event === 'exception' && idx < last ? 'warning' :
                    step.event.includes('exception') ? 'error' : ''
                ]">
            </div>
            <input type="range" min="0"
                v-bind:max="last"
                v-model.number="step"/>
        </div>
        <div id="ace-editor"></div>
    </md-card>
</template>
<script>
import AnnonationTypes from 'Source/annotations'
import Messages from 'Source/messages'
import Events from 'Source/events'

export default {
    data: function() {
        return {
            trace: undefined,
            script: '',
            exception: {},
            ace: {
                editor: {},
                markers: [],
            },
            step: undefined,
            last: undefined,
            codeChangeTimeOut: null,
            stepping: {
                timer: null,
                interval: 1000,
                active: false,
            },
        }
    },
    created: function() {
        this.$root.$on(Events.SEND_INPUT, this.send)
    },
    mounted: function() {
        this.ace.editor = ace.edit('ace-editor')
        this.ace.editor.session.setMode('ace/mode/python')
        this.ace.editor.session.on('change', this.change)
        this.ace.editor.session.setOptions({ useWorker: false })
        this.ace.editor.session.setValue(localStorage.getItem("script"))
    },
    methods: {
        change: function(delta) {
            this.$root.$emit(Events.RESET)
            localStorage.setItem("script", this.ace.editor.session.getValue())
            clearTimeout(this.codeChangeTimeOut)
            this.codeChangeTimeOut = setTimeout(() => {
                this.reset()
                this.send()
            }, 1000)
        },
        send: function(addPayload = {}) {
            const script = localStorage.getItem("script")
            const payload = Object.assign({}, { script }, addPayload)
            this.$http
                .post('http://localhost:8000/trace/', payload)
                .then(response => {
                    this.response(response.data)
                })
        },
        response: function(data) {
            this.script = data.script_lines
            this.trace = data.trace
            
            const last = this.trace.length - 1
            // Si "step" anterior es igual al "last" actual, no hay reactividad, por lo cual
            // no se invoca a render
            if(this.step === last) this.render(last)
            // (Caso normal) Por reactividad, se inicia "render"
            this.step = this.last = last
        },
        /**
         * Renderiza los elementos de traza en el editor
         * @param current Paso actual
         */
        render: function(current) {
            this.reset()
            const steps = this.trace.slice(0, current + 1)
            steps.forEach(this.renderStep)
        },
        /**
         * Renderiza los elementos gráficos del editor para el paso actual. También agrega marcadores
         * (indicadores de color y mensajes) si corresponde.
         * @param step Paso de ejecución actual
         * @param index Número de paso de ejecución
         */
        renderStep: function(step, index) {
            if(index === this.last && step.event !== 'return') {
                if(step.event === 'raw_input') {
                    this.renderPrompt(step, this.trace[index - 1])
                } else if(step.event.includes('exception')) {
                    this.renderUncaughtException(step)
                }
                this.finishRender(step)
                return
            } else if(step.event === 'exception') {
                this.renderException(step)
            }
            
            // Si es el paso actual en la ejecución paso a paso
            if(index === this.step) {
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
        renderException: function(exception) {
            const row = exception.line - 1
            this.highlight(row, exception.offset, exception.exception_msg, AnnonationTypes.WARNING)
        },
        renderUncaughtException: function(exception) {
            const row = exception.line - 1
            this.highlight(row, exception.offset, exception.exception_msg, AnnonationTypes.ERROR)
        },
        renderPrompt: function(raw_input, last_step) {
            this.$root.$emit(Events.PROMPT_INPUT, raw_input)
            const row = last_step.line - 1
            this.highlight(row, 0, Messages.PROMPT, AnnonationTypes.PROMPT)
        },
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
        play: function() {
            if(this.step == this.last) this.step = 0
            this.stepping.timer = setInterval(() => {
                this.step += 1
                if(this.step === this.last) this.pause()
            }, this.stepping.interval)
            this.stepping.active = true
        },
        pause: function() {
            clearInterval(this.stepping.timer)
            this.stepping.timer = undefined
            this.stepping.active = false
        },
        refresh: function() {
            this.$root.$emit(Events.RESET)
            this.reset()
            this.send()
        },
        reset: function() {
            this.exception = undefined
            this.ace.editor.getSession().setAnnotations([])
            this.ace.markers.map(marker => {
                this.ace.editor.session.removeMarker(marker)
            })
            this.ace.markers = []
        },
    },
    watch: {
        step: function(current) {
            this.render(current)
        },
    }
}
</script>
