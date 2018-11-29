<template>
    <input type="range" class="md-elevation-1" min="0"
        v-bind:max="stepping.last"
        v-model.number="stepping.current"
        v-if="stepping.last >= minSteps"
        @input="setStep"/>
</template>
<script>
import Events from '@/events'

export default {
    data: function() {
        return {
            minSteps: 6,
            stepping: {
                current: undefined,
                last: undefined,
            },
        }
    },
    created: function() {
        this.$root.$on(Events.UPDATE_STEPPING, (stepping) => this.stepping = stepping)
        this.$root.$on(Events.SET_STEP, (step) => this.stepping.current = step)
    },
    mounted: function() {
        this.$root.$emit(Events.REQUEST_STEPPING)
    },
    methods: {
        setStep: function() {
            this.$root.$emit(Events.SET_STEP, this.stepping.current)
        }
    },
}
</script>
