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
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Methods from '@/components/trace/methods'

export default {
    name: 'list',
    props: ['depth', 'index', 'variable', 'vertical'],
    methods: Methods
}
</script>
