<template>
    <div class="editor-ace">
        <md-progress-bar class="progress-abs-bottom"
            md-mode="determinate"
            :md-value="remaining.perc"
            v-if="remaining.perc > 0"
            :style="{ opacity: 1.25 - remaining.perc / 100 }"></md-progress-bar>
        <div id="ace-editor" class="editor-ace"></div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/editor.scss"></style>
<style lang="scss" src="@/assets/styles/ace.scss"></style>
<script>
import Events from '@/events'

export default {
    data: function() {
        return {
            ace: {
                editor: {},
                markers: [],
            },
            offline: {
                requested: false,
                script: undefined,
            },
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
        }
    },
    created: function() {
        this.$root.$on(Events.CLEAR_HIGHLIGHT, this.reset)
        this.$root.$on(Events.HIGHLIGHT, this.highlight)
        this.$root.$on(Events.SCROLL_EDITOR, (line) => {
            this.ace.editor.scrollToLine(line, true, true)
        })
        this.$on(Events.GO_OFFLINE, () => this.offline.script = this.ace.editor.session.getValue())
        this.$on(Events.GO_ONLINE, () => {
            const last_script = localStorage.getItem('script')
            if(this.offline.requested && this.offline.script !== last_script) this.send() 
        })
    },
    mounted: function() {
        this.ace.editor = ace.edit('ace-editor')
        this.ace.editor.session.setMode('ace/mode/python')
        this.ace.editor.renderer.setScrollMargin(10, 10, 10, 10)
        this.ace.editor.session.on('change', this.change)
        this.ace.editor.session.setValue(localStorage.getItem('script'))
    },
    methods: {
        /**
         * Callback para "onChange" de Ace Editor.
         */
        change: function(delta) {
            localStorage.setItem('script', this.ace.editor.session.getValue())

            if(this.isOffline && !this.offline.requested) {
                // Para enviar el código cuando se restablezca la conexión
                this.offline.requested = true
                // Eliminar marcas del editor
                this.reset()
                return
            }
            
            clearInterval(this.remaining.interval)            
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
            this.ace.editor.getSession().setAnnotations([])
            this.ace.markers.map(marker => {
                this.ace.editor.session.removeMarker(marker)
            })
            this.ace.markers = []
            this.offline.requested = false
        },
        /**
         * Emite eventos para restablecer todos los componentes de la aplicación relacionados
         * con la ejecución del código del usuario y enviar el código actual para su procesamiento
         * en el servidor.
         */
        send: function() {
            this.$root.$emit(Events.RESET)
            this.$root.$emit(Events.SEND_SCRIPT)
            this.reset()
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
        }
    }
}
</script>
