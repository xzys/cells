<template>
  <div>
    <Game />
    <GameInterface />
  </div>
</template>

<script>
import Game from './Game.vue'
import GameInterface from './components/GameInterface.vue'
import './assets/main.sass'

export default {
  name: 'App',
  components: {
    Game,
    GameInterface
  }
}
</script>

<style src="./assets/tailwind.css">
