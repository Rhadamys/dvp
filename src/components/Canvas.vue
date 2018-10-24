<template>
    <md-card>
        <md-card-media>
            <canvas id="canvas"></canvas>
        </md-card-media>
    </md-card>
</template>
<script>
export default {
    data: function() {
        return {
            canvas: undefined,
            context: undefined,
        }
    },
    mounted: function() {
        this.canvas = document.getElementById('canvas')
        this.context = this.canvas.getContext('2d')
        this.context.font = "16px monospace"
    }
}
</script>
