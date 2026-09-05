import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, RefreshControl } from 'react-native';
import { Screen, Brand, Icon, Label, Mono, Badge, Card, Tone } from '../components/ui';
import { C } from '../lib/theme';
import { Activity, AuditActivity, AuditReport, Settings } from '../lib/types';

interface Props {
  settings: Settings; audit: AuditReport | null; activities: Activity[];
  online: boolean | null; refreshing: boolean; onRefresh: () => void;
  onAudit: (a: Activity | null, claim: AuditActivity | null) => void;
}

export const STATUS_META: Record<string, { text: string; tone: Tone; icon: any }> = {
  DISCREPANCY: { text: 'DISCREPANCY', tone: 'red', icon: 'alert-triangle' },
  UNAUDITED: { text: 'NOT AUDITED', tone: 'amber', icon: 'help-circle' },
  CONFIRMED: { text: 'CONFIRMED', tone: 'green', icon: 'check-circle' },
  AUDIT_ONLY: { text: 'AUDIT ONLY', tone: 'muted', icon: 'eye' },
};
export const claimText = (a: AuditActivity) => {
  const c = a.latest_claim; if (!c) return 'No worker report';
  const st = c.event_type === 'FINISH' || c.event_type === 'QA_CLEARANCE' ? 'Completed' : c.event_type === 'HOLD' ? 'On hold' : 'In progress';
  return `${st}${a.claimed_quantity != null ? ` · ${a.claimed_quantity} ${a.unit ?? ''}` : ''}`;
};

export function AuditTodayScreen({ settings, audit, activities, online, refreshing, onRefresh, onAudit }: Props) {
  const s = audit?.summary;
  const rows = audit?.activities ?? [];
  const toAct = (r: AuditActivity): Activity => activities.find(a => a.activity_id === r.activity_id) ?? { activity_id: r.activity_id, activity_name: r.activity_name, discipline: r.discipline ?? 'CIVIL', unit_of_measure: r.unit, is_critical: r.is_critical, planned_finish: r.planned_finish };

  return (
    <Screen>
      <Brand right={<Badge text="MANAGER" tone="orange" icon="shield" />} />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 110 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={C.amber} />}>
        <Text style={st.hello}>Site audit</Text>
        <Text style={st.sub}>{settings.name} · {settings.projectId} · {online === false ? 'offline' : 'live worker claims'}</Text>

        <View style={st.stats}>
          <Stat n={s?.activities_with_claims ?? 0} l="CLAIMED" />
          <Stat n={s?.unaudited ?? 0} l="TO AUDIT" tone={s?.unaudited ? C.amber : undefined} />
          <Stat n={s?.discrepancies ?? 0} l="ISSUES" tone={s?.discrepancies ? C.red : undefined} />
          <Stat n={`${Math.round(s?.audit_coverage_pct ?? 0)}%`} l="COVERAGE" tone={C.green} />
        </View>

        <View style={st.secRow}>
          <Label style={{ marginBottom: 0 }}>WORKER CLAIMS TO VERIFY</Label>
          <View style={st.count}><Text style={{ color: C.text, fontWeight: '700' }}>{rows.length}</Text></View>
        </View>

        {!audit && <Card><Text style={{ color: C.muted, fontSize: 13 }}>Pull down to load worker claims from SATYA.</Text></Card>}
        {audit && rows.length === 0 && <Card><Text style={{ color: C.muted, fontSize: 13 }}>No worker reports yet for this project.</Text></Card>}
        {rows.map(r => {
          const m = STATUS_META[r.audit_status];
          return (
            <TouchableOpacity key={r.activity_id} activeOpacity={0.85} onPress={() => onAudit(toAct(r), r)}>
              <Card style={{ marginBottom: 12 }} accent={r.audit_status === 'DISCREPANCY' ? C.red : r.audit_status === 'UNAUDITED' ? C.amber : undefined}>
                <View style={st.row}>
                  <Mono>{r.activity_id}</Mono>
                  <Badge text={m.text} tone={m.tone} icon={m.icon} />
                </View>
                <Text style={st.actName}>{r.activity_name}</Text>
                <View style={[st.row, { marginTop: 12 }]}>
                  <View style={{ flex: 1 }}>
                    <Label style={{ marginBottom: 2, fontSize: 10 }}>CLAIMED</Label>
                    <Text style={st.val}>{claimText(r)}</Text>
                    <Mono style={{ fontSize: 11, marginTop: 2 }}>{r.latest_claim?.author} · {r.latest_claim?.observed_at?.slice(0, 10)}</Mono>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Label style={{ marginBottom: 2, fontSize: 10 }}>AUDITED</Label>
                    <Text style={[st.val, !r.latest_audit && { color: C.muted }]}>{r.latest_audit ? `${r.audited_quantity ?? '—'} ${r.unit ?? ''}` : 'Not yet'}</Text>
                    {r.variance_pct != null && <Text style={{ color: Math.abs(r.variance_pct) > 10 ? C.red : C.green, fontSize: 12, marginTop: 2 }}>{r.variance_pct > 0 ? `${r.variance_pct}% over-reported` : r.variance_pct < 0 ? `${-r.variance_pct}% under-reported` : 'Exact'}</Text>}
                  </View>
                  <Icon name="chevron-right" size={20} color={C.muted} />
                </View>
              </Card>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
      <TouchableOpacity style={st.fab} activeOpacity={0.85} onPress={() => onAudit(null, null)}>
        <Icon name="clipboard" size={18} color={C.onPrimary} /><Text style={st.fabText}>Record Audit</Text>
      </TouchableOpacity>
    </Screen>
  );
}

function Stat({ n, l, tone }: { n: number | string; l: string; tone?: string }) {
  return <View style={st.stat}><Text style={[st.statN, tone ? { color: tone } : null]}>{n}</Text><Text style={st.statL}>{l}</Text></View>;
}

const st = StyleSheet.create({
  hello: { color: C.text, fontSize: 26, fontWeight: '700', marginTop: 6 },
  sub: { color: C.muted, marginTop: 4, fontSize: 14 },
  stats: { flexDirection: 'row', marginTop: 18, borderWidth: 1, borderColor: C.border, borderRadius: 6, backgroundColor: C.surface },
  stat: { flex: 1, alignItems: 'center', paddingVertical: 14, borderRightWidth: 1, borderColor: C.border },
  statN: { color: C.text, fontSize: 20, fontWeight: '800' },
  statL: { color: C.muted, fontSize: 10, letterSpacing: 1.5, marginTop: 4 },
  secRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 28, marginBottom: 14 },
  count: { borderWidth: 1, borderColor: C.border, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 4 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  actName: { color: C.text, fontSize: 18, fontWeight: '600', marginTop: 12 },
  val: { color: C.text, fontSize: 14, fontWeight: '600' },
  fab: { position: 'absolute', right: 20, bottom: 20, flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: C.orange, paddingHorizontal: 20, paddingVertical: 16, borderRadius: 8, elevation: 4, shadowColor: '#000', shadowOpacity: 0.15, shadowRadius: 6, shadowOffset: { width: 0, height: 3 } },
  fabText: { color: C.onPrimary, fontWeight: '800', fontSize: 15 },
});
