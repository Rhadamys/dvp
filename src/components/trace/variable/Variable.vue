<template>
    <md-content class="variable">
        <div class="variable-name">
            {{ varname }}
            <md-tooltip md-direction="top">{{ varname }}</md-tooltip>
        </div>
        <div class="variable-values">
            <div class="variable-values-box"
                @mouseover="$emit('highlight', current.line)"
                @mouseout="$emit('reset')">
                <div class="variable-values-box-step selectable" @click="$emit('step', current.step)">
                    <span>{{ current.step }}</span>
                </div>
                <div class="variable-values-box-value variable-values-current selectable"
                    :class="current.class" :style="'background-color: ' + current.color"
                    @click="$emit('show', { varname, index: 0 })"
                    v-html="current.icon || current.lang">
                </div>
            </div>
            <div v-if="prevals" class="variable-values">
                <md-button class="md-icon-button md-raised md-dense"
                    v-if="prevals.length > showMax && prevalsRange.start > 0"
                    @click="prevalsRange.start -= 1">
                    <md-icon>navigate_before</md-icon>
                    <md-tooltip md-direction="left" v-if="!isMobile()">{{ prevalsRange.recent }} más recientes...</md-tooltip>
                </md-button>
                <div v-for="(prev, index) in subprevals" :key="index" class="variable-values-box"
                    @mouseover="$emit('highlight', prev.line)"
                    @mouseout="$emit('reset')">
                    <div class="variable-values-box-step selectable" @click="$emit('step', prev.step)">
                        <span>{{ prev.step }}</span>
                    </div>
                    <div class="variable-values-box-value variable-values-prev selectable"
                        :class="prev.class" :style="'background-color: ' + prev.color"
                        @click="$emit('show', { varname, index: index + prevalsRange.start + 1 })"
                        v-html="prev.icon || prev.lang">
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
</template>
<script>
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
        }
    },
    methods: {
        show: function(index = undefined) {
            this.$parent.$emit('SHOW_VAR', { index, varname: this.varname })
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
    }
}
</script>