<template>
  <div class="logger" ref="logger">
    <template v-if="!hidden">
      <div v-for="(s, i) of stmts" :key="i"
        class="px-2"
        >
        <span class="text-grey-400"
          >[{{ s.ctx.cell }}]</span>
        {{ s.msg }}
        <span v-if="s.count > 1"
          class="float-right text-grey-500"
          >x{{ s.count }}</span>
      </div>
      <div v-if="error"
        class="px-2 error-stmt"
        >
        <span class="text-red-400"
          >[Error in {{ error.ctx.cell }}]</span>
        <br>
        <span>{{ error.msg }}</span>
      </div>
    </template>
    <div>
      <div class="text-button float-left"
        @click="toggleHidden"
        >{{ hidden ? 'show' : 'hide' }}</div>
      <div class="text-button float-right"
        @click="clear"
        >clear</div>
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
      error: null,

      // so duplicate logs don't take up extra space
      countingEnabled: true,
      hidden: false,
    }
  },
  created() {
    let self = this
    eventService.bus.on(eventService.events.PRINT, self.onPrint)
    eventService.bus.on(eventService.events.ERROR, self.onError)
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
      self.stmts.push({ msg, ctx, count: 1 })
      self.scrollToBottom()
    },
    onError(msg, ctx) {
      let self = this
      self.error = { msg, ctx, error: true }
      self.scrollToBottom()
    },
    scrollToBottom() {
      let self = this
      self.$nextTick(() => {
        self.$refs.logger.scrollTop = self.$refs.logger.scrollHeight;
      })
    },
    clear() {
      let self = this
      self.stmts = []
      self.error = null
    },
    toggleHidden() {
      let self = this
      self.hidden = !self.hidden
      self.scrollToBottom()
    }
  }
}
</script>

<style lang="sass">

.logger
  @apply .bg-grey-600 .text-white .rounded
  @apply .pt-3 .pb-1 .-mt-2 .z-10
  @apply .overflow-y-scroll

  .error-stmt
    @apply .whitespace-pre .bg-red-700 .text-red-200

</style>
