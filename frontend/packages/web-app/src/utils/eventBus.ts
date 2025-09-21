type EventFun = (...args: any) => void
interface EventBus {
  $on: (event: string, listener: EventFun) => void
  $once: (event: string, listener: EventFun) => void
  $off: (event: string, listener?: EventFun) => void
  $emit: (event: string, ...args: any[]) => void
}

type EventMap = Record<string, any[]>

export class Bus<Events extends EventMap> implements EventBus {
  private listeners = new Map<keyof Events, EventFun[]>()

  $on<EventName extends keyof Events>(event: EventName, listener: (...args: Events[EventName]) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(listener)
  }

  $once<EventName extends keyof Events>(event: EventName, listener: (...args: Events[EventName]) => void): void {
    const onceFn = (...args: Events[EventName]) => {
      listener(...args)
      this.$off(event, onceFn)
    }
    this.$on(event, onceFn)
  }

  $off<EventName extends keyof Events>(event: EventName, listener?: (...args: Events[EventName]) => void): void {
    const listenerFns = this.listeners.get(event)
    if (!listenerFns)
      return
    if (!listener) {
      this.listeners.delete(event)
      return
    }
    this.listeners.set(event, listenerFns.filter(fn => fn !== listener))
  }

  $emit<EventName extends keyof Events>(event: EventName, ...args: Events[EventName]): void {
    const listenerFns = this.listeners.get(event)
    if (!listenerFns)
      return
    listenerFns.forEach(listener => listener(...args))
  }
}

export default new Bus()
