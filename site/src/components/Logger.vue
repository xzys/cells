<template>
  <div class="logger" :class="{'hidden': !stmts.length}">
    <div v-for="(s, i) of stmts"
      :key="i"
      >
      <span class="text-grey-500"
        >[{{ s.ctx.cell }}]</span>
      {{ s.msg }}
      <span v-if="s.count > 1"
        class="float-right text-grey-500"
        >x{{ s.count}}</span>
    </div>
  </div>
</template>

<script>
import eventService from '../services/eventService'

export default {
  name: 'Logger',
  data() {
    return {
      // {
      //   msg: 'log message',
      //   count: 1,
      // }
      stmts: [],

      // so duplicate logs don't take up extra space
      countingEnabled: true,
    }
  },
  created() {
    let self = this
    eventService.bus.on(eventService.events.PRINT, self.onPrint)
  },
  methods: {
    onPrint(msg, ctx) {
      let self = this
      let last = self.stmts.length ? self.stmts[self.stmts.length-1] : null
      if (self.countingEnabled &&
        last &&
        last.msg === msg &&
        last.ctx.cell == ctx.cell
      ) {
        last.count += 1
        last.ctx = ctx
        return
      }
      self.stmts.push({msg, ctx, count: 1})
    },
  }
}
</script>

<style lang="sass">

.logger
  @apply .bg-grey-600 .text-white .rounded
  @apply .font-mono .text-xs
  @apply .px-2 .pt-4 .pb-2 .-mt-2
  @apply .relative .z-10
  @apply .overflow-y-scroll

  height: 50%

  &.hidden
    height: 0


</style>
