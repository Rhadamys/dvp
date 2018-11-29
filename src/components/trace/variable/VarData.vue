<template>
    <div style="margin: auto">
        <div v-if="thisType === vartypes.DICT">
            <div :style="{ 'background-color': color() }"
                class="variable-dict">
                <dict v-for="(val, idx) in decode(variable, thisType)" :key="idx"
                    :depth="1"
                    :dkey="val[0]"
                    :variable="val[1]"
                    class="md-elevation-4">
                </dict>
            </div>
        </div>
        <div v-else-if="thisType === vartypes.LIST">
            <div v-if="variable.length > 1"
                :style="{ 'background-color': color() }"
                class="variable-list">
                <list v-for="(val, idx) in decode(variable, thisType)" :key="idx"
                    :depth="1"
                    :index="idx"
                    :variable="val"
                    class="variable-list-item md-elevation-4">
                </list>
            </div>
            <div class="variable-list-item md-elevation-4" v-else>
                <div class="variable-list-item-value variable-values-current-list">Lista vacía</div>
            </div>
        </div>
        <div v-else-if="thisType === vartypes.LIST_OF_LISTS">
            <div v-if="variable.length > 0"
                :style="{ 'background-color': color() }"
                class="variable-list-vertical">
                <list v-for="(val, idx) in decode(variable, thisType)" :key="idx"
                    :depth="1"
                    :index="idx"
                    :variable="val"
                    :vertical="true"
                    class="variable-list-vertical-item md-elevation-4">
                </list>
            </div>
            <p class="text-center" v-else>Lista vacía</p>
        </div>
        <div v-else-if="detailed && thisType === vartypes.MATRIX" class="variable-unique md-elevation-4">
            <div class="variable-unique-text variable-unique-text-input">
                <span>Matriz</span>
                <md-switch v-model="other">Ver como lista de listas</md-switch>
            </div>
            <div class="variable-unique-content">
                <div class="variable-unique-value variable-values-current-list variable-list-vertical" v-if="other">
                    <list v-for="(val, idx) in decode(variable, thisType)" :key="idx"
                        :depth="1"
                        :index="idx"
                        :variable="val"
                        :vertical="true"
                        class="variable-list-vertical-item md-elevation-4">
                    </list>
                </div>
                <div class="variable-unique-value variable-values-current-list" v-else>
                    <matrix :variable="variable"></matrix>
                </div>
            </div>
        </div>
        <matrix v-else-if="thisType === vartypes.MATRIX" :variable="variable"></matrix>
        <funct v-else-if="thisType === vartypes.FUNCTION" :variable="decode(variable, thisType)"></funct>
        <div v-else-if="detailed && (thisType === vartypes.NUMBER || thisType === vartypes.FLOAT)" class="variable-unique md-elevation-4">
            <div class="variable-unique-text variable-unique-text-input">
                <span v-if="thisType === vartypes.NUMBER">Número entero [<b class="variable-unique-type">int</b>]</span>
                <span v-else>Número de coma flotante [<b class="variable-unique-type">float</b>]</span>
                <md-switch v-if="thisType === vartypes.FLOAT || variable > 999" v-model="other" >Ver con puntos y comas</md-switch>
            </div>
            <div class="variable-unique-content">
                <div class="variable-unique-value variable-values-current-number" v-if="other">{{ decode(variable, thisType) }}</div>
                <div class="variable-unique-value variable-values-current-number" v-else>{{ variable }}</div>
            </div>
        </div>
        <div v-else-if="detailed && thisType === vartypes.STRING" class="variable-unique md-elevation-4">
            <div class="variable-unique-text variable-unique-text-input">
                <span>Cadena de caracteres [<b class="variable-unique-type">string</b>]</span>
                <md-switch v-model="other">Ver como lista</md-switch>
            </div>
            <div class="variable-unique-content">
                <div class="variable-unique-value variable-values-current-list variable-list" v-if="other">
                    <list v-for="(char, idx) in variable" :key="idx"
                        :depth="1"
                        :index="idx"
                        :variable="char"
                        class="variable-list-item md-elevation-4">
                    </list>
                </div>
                <div class="variable-unique-value variable-values-current-string" v-html="decode(variable, thisType)" v-else></div>
            </div>
        </div>
        <div v-else-if="detailed && thisType === vartypes.CHAR" class="variable-unique md-elevation-4">
            <div class="variable-unique-text">
                Caracter [<b class="variable-unique-type">char</b>]
            </div>
            <div class="variable-unique-content">
                <div class="variable-unique-value variable-values-current-char">{{ variable }}</div>
            </div>
        </div>
        <div v-else>
            <span>{{ variable }}</span>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'
import Dictionary from './types/Dictionary'
import Func from './types/Function'
import List from './types/List'
import Matrix from './types/Matrix'

export default {
    name: 'var-data',
    props: ['detailed', 'variable'],
    data: function() {
        return {
            other: false,
            thisType: this.type(this.variable),
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

