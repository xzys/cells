<template>
  <div class="ui-container fixed flex flex-row top-0 left-0 p-8 w-1/2 h-full">

    <div class="buttons-col mr-2">
      <template v-for="(pane, i) of panes">
        <div class="button-icon"
          :class="{ 'button-inactive': !pane.active }"
          @click="pane.active = !pane.active"
          :key="i"
          >
          <component v-bind:is="pane.component" class="icon"/>
        </div>
      </template>
    </div>

    <div class="flex-1 flex flex-col">
      <div class="buttons-row flex mb-2">
        <div class="button w-24"
          @click="onPlayPause">
          <IconPlay class="icon" v-if="paused" />
          <IconPause class="icon" v-else />
          {{ paused ? 'Play' : 'Pause'}}
        </div>
        <div class="button w-24"
          @click="onTest">
          <IconBeaker class="icon"/>
          Test
        </div>
        <div class="flex-1"></div>
        <div class="button-icon button-inactive">
          <IconHand class="icon"/>
        </div>
      </div>
      
      <CodeEditor
        />
    </div>
  </div>
</template>

<script>
import IconPlay from 'heroicons/outline/play.svg'
import IconPause from 'heroicons/outline/pause.svg'
import IconBeaker from 'heroicons/outline/beaker.svg'
import IconHand from 'heroicons/outline/hand.svg'

import IconTerminal from 'heroicons/outline/terminal.svg'
import IconCode from 'heroicons/outline/code.svg'
import IconChat from 'heroicons/outline/chat-alt-2.svg'
import IconSettings from 'heroicons/outline/cog.svg'

import CodeEditor from './CodeEditor'

export default {
  name: 'GameInterface',
  components: {
    IconTerminal, IconCode, IconChat, IconSettings,
    IconPlay, IconPause, IconBeaker, IconHand,
    CodeEditor
  },
  data() {
    return {
      paused: true,
      panes: [
        {
          active: true,
          component: 'IconCode',
        },
        {
          active: false,
          component: 'IconTerminal',
        },
        {
          active: false,
          component: 'IconChat',
        },
        {
          active: false,
          component: 'IconSettings',
        },
      ]
    }
  },

  methods: {
    onPlayPause() {
      let self = this
      self.paused = !self.paused
    },

    onTest() {}
  }
}
</script>

<style lang="sass">
.ui-container

  .ui-element
    @apply .rounded-md .bg-grey-800 .text-white

  .buttons-row
    .button
      @apply .mr-2
    .button:last-child
      @apply .mr-0
  .buttons-col .button
    @apply .mb-2

  .button
    @extend .ui-element
    @apply .cursor-pointer .text-center
    @apply .py-1 .px-2
    @apply .flex .flex-row .items-center .justify-center
    @apply .border .border-gray-400 .shadow-md

  .button:hover
    @apply .bg-grey-600

  .button-inactive
    @apply .bg-grey-500
    .icon path
      stroke: theme('colors.grey.300')

  .icon
    @apply .w-4 .h-4 .mr-2

  .button-icon
    @extend .button
    @apply .py-1 .px-1

    .icon
      @apply .w-6 .h-6 .mr-0 

</style>
