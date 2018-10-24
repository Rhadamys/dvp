<template>
    <div class="container md-layout md-gutter">
        <div class="md-layout-item md-size-60 md-small-size-100">
            <editor class="md-elevation-6"></editor>
        </div>
        <div class="md-layout-item visual-panel">
            <console class="md-elevation-6 io"></console>
            <anm-canvas class="canvas"></anm-canvas>
        </div>
    </div>
</template>
<script>
import Editor from '../components/Editor.vue'
import IOConsole from '../components/Console.vue'
import Canvas from '../components/Canvas.vue'

export default {
    components: {
        'editor': Editor,
        'console': IOConsole,
        'anm-canvas': Canvas,
    }
}
</script>
