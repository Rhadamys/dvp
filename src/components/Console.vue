<template>
    <md-card class="io" :class="{ 'io-minimized': hide && !expanded }">
        <md-card-actions md-alignment="space-between">
            <span class="md-title">Consola</span>
            <md-switch v-model="history.active" value="0" @change="scrollDown" :disabled="history.cached.length === 0">Historial</md-switch>
            <md-button class="md-dense console-resize" @click="$emit('resize')">
                <md-icon v-if="expanded">keyboard_arrow_up</md-icon>
                <md-icon v-else-if="hide">remove</md-icon>
                <md-icon v-else>keyboard_arrow_down</md-icon>
                <md-tooltip v-if="!isMobile()" md-direction="left">
                    {{ expanded ? messages.minimize : hide ? messages.neutral : messages.maximize }}
                </md-tooltip>
            </md-button>
        </md-card-actions>
        <md-card-content id="output" class="console" v-show="!hide || expanded">
            <div class="console-item" v-html="history.cached" v-if="history.active"></div>
            <div class="console-item" v-html="history.current" v-else></div>
            <div class="console-item console-prompt" v-show="input.request && !history.active">
                <md-field class="console-prompt-input">
                    <label>{{ input.request }}</label>
                    <md-textarea :value="input.current" @input="input.current = $event" @keyup.enter="submit(true)" id="console-input"></md-textarea>
                </md-field>
                <div class="console-prompt-send" v-if="input.request && !history.active">
                    <md-checkbox class="md-primary" v-model="input.enter">Presionar <b>"ENTER"</b> para enviar</md-checkbox>
                    <md-button class="md-primary md-dense md-raised" v-show="!input.enter" @click="submit(false)">
                        <md-icon>send</md-icon>&ensp;Enviar
                    </md-button>
                </div>
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
<script>
import Const from '@/const'
import Events from '@/events'

export default {
    props: ['hide', 'expanded'],
    data: function() {
        return {
            history: {
                active: false,
                cached: '',
                current: '',
            },
            input: {
                array: [],
                current: '',
                element: undefined,
                enter: true,
                request: undefined,
            },
            messages: Const.SIZING_MESSAGES,
        }
    },
    created: function() {
        this.$root.$on(Events.UPDATE_CONSOLE, this.update)
        this.$root.$on(Events.PROMPT_INPUT, (raw_input) => {
            this.input.request = raw_input.prompt || ' '
            
            if(this.input.array.length === 0) return
            // Centra la entrada en el input, si ya se han ingresado datos antes
            // para evitar hacer clic en cada entrada.
            this.$nextTick(() => this.input.element.focus())
        })
        this.$root.$on(Events.CLEAR_INPUT, this.reset)
        this.$root.$on(Events.RESET, () => {
            this.reset()
            this.input.array = []
            this.history.current = ''
        })
    },
    mounted: function() {
        this.input.element = document.getElementById('console-input')
    },
    methods: {
        /**
         * Callback desde Editor para actualizar la salida en la consola.
         * @param stdout Salida en el paso actual de la ejecución.
         */
        update: function({ first, stdout }) {
            this.history.current = this.stdout = stdout.replace(/\n/g, '<br>')
            this.scrollDown()

            if(this.input.request || !first) return
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
        submit: function(enterPressed) {
            if(!this.input.enter && enterPressed) return
            const breakReplace = this.input.current.replace(/\\n/g, '\n')
            const last = breakReplace.length - 1
            const withoutBreak = this.input.enter && breakReplace[last] == '\n' ? breakReplace.substr(0, last) : breakReplace
            this.history.current += this.input.request + ' ' + withoutBreak.replace(/\n/g, '<br>')
            this.input.array.push(withoutBreak)
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
