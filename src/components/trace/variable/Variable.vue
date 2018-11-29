<template>
    <div>
        <md-content class="variable">
            <div class="variable-name">
                {{ varname }}
            </div>
            <div class="variable-values">
                <div class="variable-values-box">
                    <div class="variable-values-box-step">
                        <span>Actual</span>
                    </div>
                    <div class="variable-values-box-value variable-values-current selectable"
                        :class="'variable-values-current-' + type(current)"
                        @click="show()"
                        v-html="value(current)">
                    </div>
                </div>
                <div v-if="prevals" class="variable-values">
                    <md-button class="md-icon-button md-raised md-dense"
                        v-if="prevals.length > showMax && prevalsRange.start > 0"
                        @click="prevalsRange.start -= 1">
                        <md-icon>navigate_before</md-icon>
                        <md-tooltip md-direction="left" v-if="!isMobile()">{{ prevalsRange.recent }} más recientes...</md-tooltip>
                    </md-button>
                    <div v-for="(prev, index) in subprevals" :key="index" class="variable-values-box">
                        <div class="variable-values-box-step selectable">
                            <span @click="setStep(prev.step - 1)">{{ prev.step }}</span>
                        </div>
                        <div class="variable-values-box-value variable-values-prev selectable"
                            :class="'variable-values-prev-' + type(prev.value)"
                            @click="show(index + prevalsRange.start)"
                            v-html="value(prev.value)">
                        </div>
                    </div>
                    <md-button class="md-icon-button md-raised md-dense"
                        v-if="prevals.length > showMax && prevalsRange.start < prevals.length - showMax"
                        @click="prevalsRange.start += 1">
                        <md-icon>navigate_next</md-icon>
                        <md-tooltip md-direction="left" v-if="!isMobile()">{{ prevalsRange.prev }} más anteriores...</md-tooltip>
                    </md-button>
                </div>
            </div>
        </md-content>
        <md-dialog :md-active.sync="showDialog" class="variable-dialog">
            <md-dialog-title>
                <div>
                    <span class="md-title">{{ varname }}</span>
                    <md-chip class="md-step">
                        {{ index === 0 ? 'Valor actual' : 'Valor hasta el paso ' + variable.step }}
                    </md-chip>
                </div>
                <div class="md-stepping" v-if="prevals">
                    <md-button class="md-icon-button md-dense"
                        @click="index += 1"
                        v-bind:disabled="index === prevals.length">
                        <md-icon>navigate_before</md-icon>
                        <md-tooltip md-direction="top">Anterior</md-tooltip>
                    </md-button>
                    <md-button class="md-icon-button md-dense"
                        @click="index -= 1"
                        v-bind:disabled="index === 0">
                        <md-icon>navigate_next</md-icon>
                        <md-tooltip md-direction="top">Siguiente</md-tooltip>
                    </md-button>
                </div>
            </md-dialog-title>
            <md-dialog-content>
                <var-data :detailed="true" :variable="variable.value"></var-data>
            </md-dialog-content>
            <md-dialog-actions>
                <md-button class="md-primary" @click="showDialog = false">Cerrar</md-button>
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Events from '@/events'
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'
import VarData from './VarData'

export default {
    props: ['current', 'prevals', 'varname'],
    data: function() {
        return {
            index: undefined,
            prevalsRange: {
                prev: 0,
                recent: 0,
                start: 0,
            },
            showDialog: false,
            variable: {
                step: undefined,
                value: undefined,
            },
            vartypes: VarTypes,
        }
    },
    components: {
        'var-data': VarData,
    },
    methods: {
        ...Methods,
        show: function(index) {
            this.index = index === undefined ? 0 : index + 1
            this.setVar()
            this.showDialog = true
        },
        setStep: function(step) {
            this.$root.$emit(Events.SET_STEP, step)
        },
        setVar: function() {
            if(this.prevals) {
                const selected = this.index > 0 ? this.prevals[this.index - 1] : this.current
                const value = selected.value || selected
                this.variable.step = selected.step
                this.variable.value = value
            } else
                this.variable.value = this.current
        },
    },
    computed: {
        showMax: function() {
            const bp = this.bp[this.$mq]
            return bp === this.bp.xxsmall ? 4 :
                   bp === this.bp.xsmall ? 8 :
                   bp === this.bp.small ? 10 :
                   bp === this.bp.medium ? 6 :
                   bp === this.bp.large ? 10 : 16
        },
        subprevals: function() {
            const len = this.prevals.length
            const end = this.prevalsRange.start + this.showMax
            this.prevalsRange.recent = this.prevalsRange.start
            this.prevalsRange.prev = len - end
            return this.prevals.slice(this.prevalsRange.start, end)
        }
    },
    watch: {
        index: function() {
            this.setVar()
        },
    }
}
</script>