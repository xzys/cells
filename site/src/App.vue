<template>
  <div class="game-container">
    <Game />
    <div class="ui-container">
      <div class="code-container">
        <textarea id="code"></textarea>
      </div>
    </div>
    <div class="debug-text" id="debug-text">TEST</div>
  </div>
</template>

<script>
import Game from './Game.vue'
import './assets/main.sass'

export default {
  name: 'App',
  components: {
    Game
  }
}
</script>
