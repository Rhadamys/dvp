<template>
    <div>
        <div class="variable-dict-content md-elevation-4" v-for="(value, key) in variable" :key="key">
            <div class="variable-dict-key">
                <span>{{ key }}:</span>
            </div>
            <div class="variable-dict-value" :class="value.type">
                <var-data :depth="depth + 1" :variable="value"></var-data>
            </div>
        </div>
    </div>
</template>
<script>
export default {
    name: 'dict',
    props: ['depth', 'variable'],
}
</script>
