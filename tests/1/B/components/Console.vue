<template>
    <md-card class="io md-scrollbar">
        <md-card-media class="console">
            <div v-for="(line, lineno) in stdout" :key="lineno">{{ line }}</div>
            <div class="console-prompt" v-if="input.request">
                <div>{{ input.request }}</div>
                <input type="text"
                    v-model="input.current"
                    v-on:keyup.enter="submit"/>
            </div>
        </md-card-media>
    </md-card>
</template>
<script>
import Events from 'Source/events'

export default {
    data: function() {
        return {
            stdout: [],
            input: {
                request: undefined,
                current: '',
                array: [], 
            },
        }
    },
    created: function() {
        this.$root.$on(Events.UPDATE_CONSOLE, (stdout) => {
            this.stdout = stdout.split('\n')
        })
        this.$root.$on(Events.PROMPT_INPUT, (raw_input) => {
            this.input.request = raw_input.prompt
            if(this.stdout.length > 1) this.stdout.pop()
        })
        this.$root.$on(Events.CLEAR_INPUT, this.reset)
        this.$root.$on(Events.RESET, () => {
            this.reset()
            this.input.array = []
        })
    },
    methods: {
        submit: function() {
            this.stdout.push(this.input.request + ' ' + this.input.current)
            this.input.array.push(this.input.current)
            this.$root.$emit(Events.SEND_INPUT, { raw_input_json: this.input.array })
            this.reset()
        },
        reset: function() {
            this.input.request = undefined
            this.input.current = ''
        }
    }
}
</script>
