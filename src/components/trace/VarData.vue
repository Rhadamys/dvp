<template>
    <div style="margin: auto">
        <div v-if="type(variable) === vartypes.DICT">
            <div :style="{ 'background-color': color() }"
                class="variable-dict">
                <dict v-for="(val, idx) in decode(variable)" :key="idx"
                    :depth="1"
                    :dkey="val[0]"
                    :variable="val[1]"
                    class="md-elevation-4">
                </dict>
            </div>
        </div>
        <div v-else-if="type(variable) === vartypes.LIST">
            <div v-if="variable.length > 0"
                :style="{ 'background-color': color() }"
                class="variable-list">
                <list v-for="(val, idx) in decode(variable)" :key="idx"
                    :depth="1"
                    :index="idx"
                    :variable="val"
                    class="variable-list-item md-elevation-4">
                </list>
            </div>
            <p class="text-center" v-else>Lista vacía</p>
        </div>
        <div v-else-if="type(variable) === vartypes.LIST_OF_LISTS">
            <div v-if="variable.length > 0"
                :style="{ 'background-color': color() }"
                class="variable-list-vertical">
                <list v-for="(val, idx) in decode(variable)" :key="idx"
                    :depth="1"
                    :index="idx"
                    :variable="val"
                    :vertical="true"
                    class="variable-list-vertical-item md-elevation-4">
                </list>
            </div>
            <p class="text-center" v-else>Lista vacía</p>
        </div>
        <matrix v-else-if="type(variable) === vartypes.MATRIX" :variable="variable"></matrix>
        <funct v-else-if="type(variable) === vartypes.FUNCTION" :variable="decode(variable)"></funct>
        <div v-else>
            <span>{{ value(variable) }}</span>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'
import Dictionary from '@/components/trace/types/Dictionary'
import Func from '@/components/trace/types/Function'
import List from '@/components/trace/types/List'
import Matrix from '@/components/trace/types/Matrix'

export default {
    name: 'var-data',
    props: ['variable'],
    data: function() {
        return {
            vartypes: VarTypes,
        }
    },
    components: {
        'dict': Dictionary,
        'list': List,
        'matrix': Matrix,
        'funct': Func,
    },
    methods: Methods
}
</script>

