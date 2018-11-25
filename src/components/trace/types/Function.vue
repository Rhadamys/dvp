<template>
    <div class="variable-function">
        <div class="gorup-vertical variable-function-identifier md-elevation-4">
            <div class="group-vertical-title">
                <span>Identificador</span>
            </div>
            <div class="group-vertical-content">{{ variable.name }}</div>
        </div>
        <div class="variable-function-raw">(</div>
        <div class="variable-function-params group-vertical md-evelation-4">
            <div class="group-vertical-title">
                <span>Parámetros</span>
            </div>
            <div class="group-vertical-content group-horizontal">
                <div v-for="(param, index) in variable.params" :key="index"
                    class="group-horizontal">
                    <div class="variable-function-param md-elevation-4">
                        <span>{{ param }}</span>
                    </div>
                    <div class="variable-function-raw" v-if="index < variable.params.length - 1">,</div>
                </div>
            </div>
        </div>
        <div class="variable-function-raw">)</div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Methods from '@/components/trace/methods'

export default {
    props: ['variable'],
    methods: Methods,
}
</script>

