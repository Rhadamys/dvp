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
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Methods from '@/components/trace/methods'

export default {
    name: 'dict',
    props: ['depth', 'dkey', 'variable'],
    methods: Methods,
}
</script>
