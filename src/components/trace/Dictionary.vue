<template>
    <div class="variable-dict-content">
        <div class="variable-dict-key">
            <span>{{ dkey }}:</span>
        </div>
        <div class="variable-dict-value" 
            :class="'variable-values-current-' + type(variable)">
            <var-data :variable="variable"></var-data>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'

export default {
    name: 'dict',
    props: ['depth', 'dkey', 'variable'],
    data: function() {
        return {
            vartypes: VarTypes,
        }
    },
    methods: Methods,
}
</script>
