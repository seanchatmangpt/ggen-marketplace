export interface OcelObject {
  id: string;
  type: string;
  attributes: Record<string, unknown>;
}

export interface OcelEvent {
  id: string;
  activity: string;
  timestamp: number;
  objectIds: string[];
  attributes: Record<string, unknown>;
}

export interface EmitEventOptions {
  objectIds?: string[];
  timestamp?: number | Date;
  attributes?: Record<string, unknown>;
}

export class Pm4Session {
  private objects = new Map<string, OcelObject>();
  private events: OcelEvent[] = [];

  registerObject(id: string, type: string, attributes: Record<string, unknown> = {}): void {
    this.objects.set(id, { id, type, attributes });
  }

  emitEvent(id: string, activity: string, opts: EmitEventOptions = {}): void {
    const rawTs = opts.timestamp ?? Date.now();
    const timestamp = typeof rawTs === 'number' ? rawTs : rawTs.getTime();
    this.events.push({
      id,
      activity,
      timestamp,
      objectIds: opts.objectIds ?? [],
      attributes: opts.attributes ?? {},
    });
  }

  getTrace(): string[] {
    return this.events.map((e) => e.activity);
  }

  getEvents(): readonly OcelEvent[] {
    return this.events;
  }

  getObjects(): ReadonlyMap<string, OcelObject> {
    return this.objects;
  }

  reset(): void {
    this.objects.clear();
    this.events = [];
  }

  toOcel2Json(): string {
    const eventTypes: Record<string, Record<string, string>> = {};
    const eventsOut: Record<string, unknown>[] = [];

    for (const e of this.events) {
      if (!eventTypes[e.activity]) {
        eventTypes[e.activity] = {};
      }
      for (const [k, v] of Object.entries(e.attributes)) {
        eventTypes[e.activity][k] = typeof v;
      }
      eventsOut.push({
        id: e.id,
        type: e.activity,
        time: new Date(e.timestamp).toISOString(),
        attributes: e.attributes,
        relationships: e.objectIds.map((oid) => ({ object_id: oid, qualifier: 'target' })),
      });
    }

    const objectsOut: Record<string, unknown> = {};
    for (const [id, obj] of this.objects.entries()) {
      objectsOut[id] = {
        type: obj.type,
        attributes: obj.attributes,
      };
    }

    return JSON.stringify(
      {
        event_types: eventTypes,
        objects: objectsOut,
        events: eventsOut,
      },
      null,
      2
    );
  }
}
