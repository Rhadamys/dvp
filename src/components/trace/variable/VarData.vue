<template>
    <div style="margin: auto">
        <dict v-if="variable.type === vartypes.DICT" 
            :depth="depth"
            :variable="variable.value"
            class="variable-dict" 
            :style="{ 'background-color': color(depth) }">
        </dict>
        <div v-else-if="variable.type === vartypes.LIST">
            <list v-if="variable.value.length > 0"
                :depth="depth"
                :variable="variable.value"
                class="variable-list variable-list-horizontal" 
                :style="{ 'background-color': color(depth) }">
            </list>
            <div class="variable-list-item md-elevation-4" v-else>
                <div class="variable-list-item-value list">Lista vacía</div>
            </div>
        </div>
        <div v-else-if="variable.type === vartypes.LIST_OF_LISTS">
            <list v-if="variable.value.length > 0"
                :depth="depth"
                :variable="variable.value"
                :vertical="true"
                class="variable-list variable-list-vertical" 
                :style="{ 'background-color': color(depth) }">
            </list>
            <p class="text-center" v-else>Lista vacía</p>
        </div>
        <div v-else-if="detailed && variable.type === vartypes.MATRIX" class="variable-unique md-elevation-4">
            <div class="variable-unique-text variable-unique-text-input">
                <span>Matriz</span>
                <md-switch v-model="other">Ver como lista de listas</md-switch>
            </div>
            <div class="variable-unique-content">
                <div class="md-elevation-4 variable-unique-value list variable-list-vertical" v-if="other">
                    <list :depth="depth"
                        :variable="variable.value"
                        :vertical="true"
                        class="variable-list variable-list-vertical" 
                        :style="{ 'background-color': color(depth) }">
                    </list>
                </div>
                <div class="md-elevation-4 variable-unique-value list" v-else>
                    <matrix :variable="variable.value" :style="{ 'background-color': color(depth) }"></matrix>
                </div>
            </div>
        </div>
        <matrix v-else-if="variable.type === vartypes.MATRIX" :variable="variable.value" :style="{ 'background-color': color(depth) }"></matrix>
        <funct v-else-if="variable.type === vartypes.FUNCTION" :variable="variable.value"></funct>
        <div v-else-if="detailed && (variable.type === vartypes.NUMBER || variable.type === vartypes.FLOAT)" class="variable-unique md-elevation-4">
            <div class="variable-unique-text variable-unique-text-input">
                <span v-if="variable.type === vartypes.NUMBER">Número entero [<b class="variable-unique-type">int</b>]</span>
                <span v-else>Número de coma flotante [<b class="variable-unique-type">float</b>]</span>
                <md-switch v-if="variable.alternative" v-model="other" >Ver con puntos y comas</md-switch>
            </div>
            <div class="variable-unique-content">
                <div class="md-elevation-4 variable-unique-value number" v-if="other">{{ variable.alternative }}</div>
                <div class="md-elevation-4 variable-unique-value number" v-else>{{ variable.value }}</div>
            </div>
        </div>
        <div v-else-if="detailed && variable.type === vartypes.STRING" class="variable-unique md-elevation-4">
            <div class="variable-unique-text variable-unique-text-input">
                <span>Cadena de caracteres [<b class="variable-unique-type">str</b>]</span>
                <md-switch v-model="other">Ver como lista</md-switch>
            </div>
            <div class="variable-unique-content">
                <list class="md-elevation-4 variable-unique-value list variable-list" v-if="other"
                    :depth="1" :variable="variable.alternative"></list>
                <div class="md-elevation-4 variable-unique-value string" v-html="variable.parsed" v-else></div>
            </div>
        </div>
        <div v-else-if="detailed && variable.type === vartypes.CHAR" class="variable-unique md-elevation-4">
            <div class="variable-unique-text">
                Caracter [<b class="variable-unique-type">char</b>]
            </div>
            <div class="variable-unique-content">
                <div class="md-elevation-4 variable-unique-value char char-parsed" v-if="variable.parsed">{{ variable.parsed }}</div>
                <div class="md-elevation-4 variable-unique-value char" v-else>{{ variable.value }}</div>
            </div>
        </div>
        <div v-else-if="detailed && variable.type === vartypes.BOOLEAN" class="variable-unique md-elevation-4">
            <div class="variable-unique-text">
                Lógico [<b class="variable-unique-type">bool</b>]
            </div>
            <div class="variable-unique-content">
                <div class="md-elevation-4 variable-unique-value boolean" :class="variable.bool">{{ variable.value }}</div>
            </div>
        </div>
        <div v-else>
            <span>{{ variable.value }}</span>
        </div>
    </div>
</template>
<script>
import VarTypes from '@/vartypes'
import Dictionary from './types/Dictionary'
import Func from './types/Function'
import List from './types/List'
import Matrix from './types/Matrix'

export default {
    name: 'var-data',
    props: ['depth', 'detailed', 'variable'],
    data: function() {
        return {
            other: false,
            vartypes: VarTypes,
        }
    },
    components: {
        'dict': Dictionary,
        'list': List,
        'matrix': Matrix,
        'funct': Func,
    },
    methods: {
        color: function(depth = 0) {
            const base = 60 + depth * 20
            return 'rgb(' + base + ', ' + base + ', ' + (base + 10) + ')'
        },
    }
}
</script>

