import { ref, watch, onMounted, onUnmounted } from 'vue'

export function useActivityClock(active) {
    const now = ref(Date.now())
    let timer
    const stop = () => { clearInterval(timer); timer = null }
    onMounted(() => {
        watch(active, running => {
            stop()
            now.value = Date.now()
            if (running) timer = setInterval(() => { now.value = Date.now() }, 1000)
        }, { immediate: true })
    })
    onUnmounted(stop)
    return now
}
