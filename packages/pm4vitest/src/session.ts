/**
 * pm4vitest — process-bound OCEL session tracking.
 *
 * Pm4Session collects events and objects during a vitest run, forming an
 * OCEL-shaped (IEEE 1849-2) event log that conformance and SLA assertions
 * replay against.
 */

export interface OcelObject {
  id: string;
  type: string;
  attributes: Record<string, unknown>;
}

export interface OcelEvent {
  id: string;
  activity: string;
  time: Date;
  attributes: Record<string, unknown>;
  /** object ids this event relates to, with qualification */
  relationships: Array<{ objectId: string; qualifier: string }>;
}

export interface EmitEventOptions {
  timestamp?: Date;
  attributes?: Record<string, unknown>;
  /** related object ids; qualifier defaults to "related" */
  objectIds?: string[];
}

export interface TraceEvent {
  eventId: string;
  activity: string;
  time: Date;
  attributes: Record<string, unknown>;
}

export class Pm4Session {
  readonly objects: OcelObject[] = [];
  readonly events: OcelEvent[] = [];
  readonly objectTypes = new Set<string>();
  readonly eventTypes = new Set<string>();

  registerObject(objId: string, objType: string, attrs: Record<string, unknown> = {}): this {
    this.objectTypes.add(objType);
    this.objects.push({ id: objId, type: objType, attributes: { ...attrs } });
    return this;
  }

  emitEvent(eventId: string, activity: string, opts: EmitEventOptions = {}): this {
    this.eventTypes.add(activity);
    const time = opts.timestamp ?? new Date();
    const relationships = (opts.objectIds ?? []).map((objectId) => ({
      objectId,
      qualifier: 'related',
    }));
    this.events.push({
      id: eventId,
      activity,
      time,
      attributes: { ...(opts.attributes ?? {}) },
      relationships,
    });
    return this;
  }

  /** Sequential activity trace (projected from the OCEL event log, in emission order). */
  getTrace(): TraceEvent[] {
    return this.events.map((e) => ({
      eventId: e.id,
      activity: e.activity,
      time: e.time,
      attributes: e.attributes,
    }));
  }
}
