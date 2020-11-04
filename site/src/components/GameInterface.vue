<template>
  <div class="ui-container fixed flex flex-row top-0 left-0 p-2 h-full w-full">

    <div class="buttons-col mr-2">
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
  </div>
</template>

<script>
import IconTerminal from 'heroicons/outline/terminal.svg'
import IconCode from 'heroicons/outline/code.svg'
import IconChat from 'heroicons/outline/chat-alt-2.svg'
import IconSettings from 'heroicons/outline/cog.svg'

import CodeEditor from './CodeEditor'

export default {
  name: 'GameInterface',
  components: {
    IconTerminal, IconCode, IconChat, IconSettings,
    CodeEditor
  },
  data() {
    return {
      panes: [
        {
          active: true,
          icon: 'IconCode',
        },
        {
          active: false,
          icon: 'IconTerminal',
        },
        {
          active: false,
          icon: 'IconChat',
        },
        {
          active: false,
          icon: 'IconSettings',
        },
      ]
    }
  },

  methods: {
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
    @apply .shadow-md

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
