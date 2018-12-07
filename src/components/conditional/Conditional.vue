<template>
    <md-card class="conditional" md-theme="default-light" v-if="conditional">
        <md-card-actions class="conditional-header">
            <md-button class="conditional-header-collapse" @click="show = !show">
                <md-icon v-if="show">keyboard_arrow_down</md-icon>
                <md-icon v-else>keyboard_arrow_up</md-icon>
                &ensp;Expresión condicional
                <md-chip :class="'conditional-chip conditional-chip-' + conditional.result" v-if="typeof conditional.result === 'boolean'">{{ conditional.result ? 'Verdadero' : 'Falso' }}</md-chip>
            </md-button>
            <div v-if="show && conditional.trace.length > 1">
                <md-button class="conditional-header-stepper" :disabled="current === 0" @click="current -= 1">
                    <md-icon>navigate_before</md-icon>
                </md-button>
                <md-button class="conditional-header-stepper" :disabled="current === conditional.trace.length - 1" @click="current += 1">
                    <md-icon>navigate_next</md-icon>
                </md-button>
            </div>
        </md-card-actions>
        <div class="conditional-content" id="conditional-content" v-if="show" :style="stepper ? 'padding-bottom: 12px !important' : ''">
            <input type="range" class="conditional-stepper" min="0"
                v-bind:max="conditional.trace.length - 1"
                v-model.number="current"
                v-if="stepper"/>
            <div class="conditional-expression" id="expression-container">
                <expression :current="step.tree"
                    :depth="0"
                    :parsed="step.expression"
                    :result="step.result"
                    :tree="''"
                    class="expression-inner"></expression>
            </div>
        </div>
    </md-card>
</template>
<style lang="scss" src="@/assets/styles/conditional.scss"></style>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Events from '@/events'
import Methods from '@/components/trace/methods'
import Expression from './Expression'

export default {
    data: function() {
        return {
            conditional: undefined,
            current: 0,
            show: true,
        }
    },
    components: {
        'expression': Expression,
    },
    created: function() {
        this.$root.$on(Events.SET_CONDITIONAL, cond => {
            this.conditional = cond
            this.current = 0
            this.$root.$emit(Events.RESIZE_EDITOR)
        })
    },
    methods: Methods,
    computed: {
        step: function() {
            this.$nextTick(() => {
                const container = document.getElementById('expression-container')
                container.scrollLeft = 0
                const expression = document.getElementsByClassName('expression-current')[0]
                const rect = expression.getBoundingClientRect()
                const width = container.getBoundingClientRect().width
                container.scrollLeft = (rect.x + (rect.width - width) / 2) / 2
            })
            return this.conditional.trace[this.current]
        },
        stepper: function() {
            return this.conditional ? this.conditional.trace.length > 2 : false
        },
    },
    watch: {
        show: function() {
            this.$root.$emit(Events.RESIZE_EDITOR)
        }
    }
}
</script>
