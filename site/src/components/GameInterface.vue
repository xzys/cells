<template>
  <div class="ui-container">
    <div class="buttons-col mr-2">
      <div class="button-icon play-pause-button"
        :class="{'paused': paused}"
        @click="onPlayPause">
        <IconPlay class="icon" v-if="paused" />
        <IconPause class="icon" v-else />
        <!-- {{ paused ? 'Play' : 'Pause'}} -->
      </div>

      <template v-for="(pane, i) of panes">
        <div class="button-icon"
          :class="{ 'button-inactive': !pane.active }"
          @click="pane.active = !pane.active"
          :key="i"
          >
          <component v-bind:is="pane.icon" class="icon"/>
        </div>
      </template>
    </div>

    <CodeEditor :class="{'hidden': !panes[0].active}"
      />
    <div class="flex-1"></div>

    <!-- floating elements -->
    <CellTooltip/>
  </div>
</template>

<script>
import IconPlay from 'heroicons/solid/play.svg'
import IconPause from 'heroicons/solid/pause.svg'
import IconTerminal from 'heroicons/outline/terminal.svg'
import IconCode from 'heroicons/outline/code.svg'
import IconChat from 'heroicons/outline/chat-alt-2.svg'
import IconSettings from 'heroicons/outline/cog.svg'

import CodeEditor from './CodeEditor'
import eventService from '../services/eventService'

export default {
  name: 'GameInterface',
  components: {
    IconPlay, IconPause,
    IconTerminal, IconCode, IconChat, IconSettings,
    CodeEditor
  },
  data() {
    return {
      panes: [
        {
          active: false,
          icon: 'IconTerminal',
        },
        /*
        {
          active: false,
          icon: 'IconCode',
        },
        {
          active: false,
          icon: 'IconChat',
        },
        */
        {
          active: false,
          icon: 'IconSettings',
        },
      ],
      paused: true,
      selected: null,
    }
  },
  created() {
    let self = this
    // when ready send initial script
    eventService.bus.on(eventService.events.ON_READY, self.onPlayPause)
    // pause on error
    eventService.bus.on(eventService.events.ERROR, self.onError)
    eventService.bus.on(eventService.events.SELECT_CELL, self.onSelectCell)
  },

  methods: {
    onPlayPause() {
      let self = this
      self.paused = !self.paused
      const e = self.paused ?
        eventService.events.PAUSE_WORLD :
        eventService.events.PLAY_WORLD
      eventService.bus.emit(e)
    },
    onError() {
      let self = this
      if (!self.paused) {
        self.onPlayPause()
      }
    },
    onSelectCell(cell) {
      let self = this
      self.selected = {
        name: cell.name
      }
    }
  }
}
</script>

<style lang="sass">
.ui-container
  @apply .fixed .top-0 .left-0 .p-2 .h-full .w-full
  @apply .flex .flex-row
  @apply .pointer-events-none

  .ui-element
    @apply .rounded-md .bg-grey-800 .text-white
    @apply .pointer-events-auto

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
    @apply .shadow-md

    &:hover
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
      @apply .w-4 .h-4 .mr-0 

  .text-button
    @apply .text-grey-200 .font-mono .text-xs
    @apply .cursor-pointer .px-2

    &:hover
      @apply .text-grey-100


  // special case play pause, needs important for specificity
  .play-pause-button
    @apply .bg-green-600 #{!important}
    &:hover
      @apply .bg-green-500 #{!important}

    &.paused
      @apply .bg-red-600 #{!important}
      &:hover
        @apply .bg-red-500 #{!important}

</style>
