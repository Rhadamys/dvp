<template>
    <div class="editor-ace">
        <md-progress-bar class="progress-abs-bottom"
            md-mode="determinate"
            :md-value="remaining.perc"
            v-if="remaining.perc > 0"
            :style="{ opacity: 1.25 - remaining.perc / 100 }"></md-progress-bar>
        <div id="ace-editor" style="height: 100%"></div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/editor.scss"></style>
<style lang="scss" src="@/assets/styles/ace.scss"></style>
<script>
import Const from '@/const'
import Events from '@/events'

export default {
    data: function() {
        return {
            ace: {
                editor: {},
                markers: [],
            },
            firstRun: true,
            /**
             * Timer para enviar código automáticamente al servidor luego de cumplirse
             * un breve periodo de tiempo sin realizar modificaciones en el editor, es
             * decir, cuando el usuario deja de escribir.
             */
            remaining: {
                interval: undefined,
                perc: 0,
                step: 100,
                time: 0,
            },
            requested: false,
            waitTime: this.isMobile() ? Const.TIME_MOBILE : Const.TIME_DESKTOP,
        }
    },
    created: function() {
        this.$root.$on(Events.CLEAR_HIGHLIGHT, this.reset)
        this.$root.$on(Events.HIGHLIGHT, this.highlight)
        this.$root.$on(Events.RESIZE_EDITOR, () => this.$nextTick(() => { this.ace.editor.resize(true) }))
        this.$root.$on(Events.SCROLL_EDITOR, line => this.ace.editor.scrollToLine(line, true, true))
        this.$root.$on(Events.SET_SCRIPT, script => this.ace.editor.session.setValue(script))
        this.$on(Events.GO_ONLINE, () => { if(this.requested) this.send() })
    },
    mounted: function() {
        this.ace.editor = ace.edit('ace-editor')
        this.ace.editor.session.setMode('ace/mode/python')
        this.ace.editor.session.on('change', this.change)
        this.ace.editor.session.setValue(localStorage.getItem('script'))
        this.ace.editor.setOptions({ autoScrollEditorIntoView: true })
    },
    methods: {
        /**
         * Callback para "onChange" de Ace Editor.
         */
        change: function(delta) {
            this.reset() // Elimina marcas del editor
            const last = localStorage.getItem('script')
            const current = this.ace.editor.session.getValue()
            if((current === last && !this.firstRun) || current === undefined || current.length === 0) return

            if(this.isOffline) {
                // Para enviar el código cuando se restablezca la conexión
                this.requested = true
                return
            }
                     
            this.remaining.perc = 100
            this.remaining.time = this.waitTime
            this.remaining.interval = setInterval(this.tick, this.remaining.step)
        },
        /**
         * Resalta una línea en el editor con un mensaje.
         * @param row Línea del código
         * @param column Columna del código
         * @param text Texto del mensaje
         * @param type Tipo de mensaje
         */
        highlight: function({ row, column, text, type }) {
            const annotations = this.ace.editor.getSession().getAnnotations()
            this.ace.editor.getSession().setAnnotations([...annotations, { row, column, text, type }])
            const Range = ace.require('ace/range').Range
            const marker_id = this.ace.editor.session.addMarker(new Range(row, 0, row, 1), type, 'fullLine')
            this.ace.markers.push(marker_id)
        },
        /**
         * Restablece las marcas del editor.
         */
        reset: function() {
            this.remaining.perc = 0
            this.remaining.time = undefined
            clearInterval(this.remaining.interval)

            this.ace.editor.getSession().setAnnotations([])
            this.ace.markers.map(marker => {
                this.ace.editor.session.removeMarker(marker)
            })
            this.ace.markers = []
            this.requested = false
        },
        /**
         * Emite eventos para restablecer todos los componentes de la aplicación relacionados
         * con la ejecución del código del usuario y enviar el código actual para su procesamiento
         * en el servidor.
         */
        send: function() {
            localStorage.setItem('script', this.ace.editor.session.getValue())
            this.firstRun = false
            this.$root.$emit(Events.RESET)
            this.$root.$emit(Events.SEND_SCRIPT)
        },
        /**
         * Este procedimiento se ejecuta en cada tick del intervalo de cuenta regresiva
         * una vez que se modifica el código.
         */
        tick: function() {
            this.remaining.time -= this.remaining.step
            this.remaining.perc = this.remaining.time * 100 / this.waitTime

            if(this.remaining.perc > 0) return
            clearInterval(this.remaining.interval)
            this.send()
        },
    }
}
</script>
