<template>
    <div>
        <div v-for="(item, idx) in variable" :key="idx" class="md-elevation-4" :class="className + 'item'">
            <div :class="className + 'item-index'">
                <span>{{ idx }}</span>
            </div>
            <div :class="[className + 'item-value', item.type]">
                <var-data :depth="depth + 1" :variable="item"></var-data>
            </div>
        </div>
    </div>
</template>
<script>
export default {
    name: 'list',
    props: ['depth', 'variable', 'vertical'],
    computed: {
        className: function() {
            return 'variable-list-' + (this.vertical ? 'vertical-' : 'horizontal-')
        }
    }
}
</script>
