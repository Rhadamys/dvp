<template>
    <div>
        <div :class="'variable-list-' + (vertical ? 'vertical-' : '') + 'item-index'">
            <span>{{ index }}</span>
        </div>
        <div :class="['variable-list-' + (vertical ? 'vertical-' : '') + 'item-value', 'variable-values-current-' + type(variable)]">
            <var-data :variable="variable"></var-data>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'

export default {
    name: 'list',
    props: ['depth', 'index', 'variable', 'vertical'],
    data: function() {
        return {
            vartypes: VarTypes,
        }
    },
    methods: Methods
}
</script>
