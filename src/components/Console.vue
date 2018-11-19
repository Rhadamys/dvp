<template>
    <md-card class="io md-scrollbar" md-theme="console">
        <md-card-actions md-alignment="space-between">
            <span class="md-title">Consola</span>
            <md-switch v-model="history.active" value="0" v-on:change="setOut">Historial</md-switch>
        </md-card-actions>
        <md-card-content id="output" class="console">
            <div v-html="stdout"></div>
            <div class="console-prompt" v-if="input.request && !history.active">
                <div>{{ input.request }}</div>
                <input type="text"
                    v-model="input.current"
                    v-on:keyup.enter="submit"/>
            </div>
            <md-button class="md-fab md-mini console-empty"
                v-if="history.active && history.cached.length > 0"
                @click="clearHistory">
                <md-icon>delete</md-icon>
                <md-tooltip md-direction="left">Limpiar historial</md-tooltip>
            </md-button>
        </md-card-content>
    </md-card>
</template>
<style lang="scss" src="@/assets/styles/console.scss"></style>
<script>
import Events from '@/events'

export default {
    data: function() {
        return {
            stdout: '',
            history: {
                active: false,
                cached: '',
                current: '',
            },
            input: {
                request: undefined,
                current: '',
                array: [], 
            }
        }
    },
    created: function() {
        this.$root.$on(Events.UPDATE_CONSOLE, this.update)
        this.$root.$on(Events.PROMPT_INPUT, (raw_input) => {
            this.input.request = raw_input.prompt
        })
        this.$root.$on(Events.CLEAR_INPUT, this.reset)
        this.$root.$on(Events.RESET, () => {
            this.reset()
            this.input.array = []
        })
    },
    mounted: function() {
    },
    methods: {
        /**
         * Callback desde Editor para actualizar la salida en la consola.
         * @param stdout Salida en el paso actual de la ejecución.
         */
        update: function(stdout) {
            this.history.current = this.stdout = stdout.replace(/\n/g, '<br>')
            this.scrollDown()

            if(this.input.request) return
            this.history.cached += '<b><i style="color: grey">' + new Date().toString() + '</i></b><br>'
            this.history.cached += this.stdout
            this.history.cached += '<br>'
        },
        /**
         * Limpia el historial de salida.
         */
        clearHistory: function() {
            this.history.cached = ''
            this.history.active = false
            this.setOut()
        },
        /**
         * Define la salida que se mostrará en la consola. Si history.active es true, entonces
         * se mostrará el historial, sino, se mostrará la salida generada en la ejecución actual.
         */
        setOut: function() {
            this.stdout = this.history.active ? this.history.cached : this.history.current
            this.scrollDown()
        },
        /**
         * Hace scroll a la consola hasta el final, para mostrar las salidas más recientes.
         */
        scrollDown: function() {
            this.$nextTick(() => {
                const output = document.getElementById('output')
                output.scrollTop = output.scrollHeight
            })
        },
        /**
         * Envía los datos ingresados por el usuario en el input para ser procesados
         * por el servidor y continuar la ejecución.
         */
        submit: function() {
            this.stdout += this.input.request + ' ' + this.input.current
            this.input.array.push(this.input.current)
            this.$root.$emit(Events.SEND_INPUT, { raw_input_json: this.input.array })
            this.reset()
        },
        reset: function() {
            this.input.request = undefined
            this.input.current = ''
            this.history.active = false
        }
    }
}
</script>
