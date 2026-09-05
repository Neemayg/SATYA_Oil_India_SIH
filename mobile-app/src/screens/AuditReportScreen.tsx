import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, RefreshControl } from 'react-native';
import { Screen, Brand, Icon, Label, Mono, Badge, Card, Button } from '../components/ui';
import { C } from '../lib/theme';
import { AuditActivity, AuditReport, Observation } from '../lib/types';
import { STATUS_META, claimText } from './AuditTodayScreen';

interface Props { audit: AuditReport | null; mine: Observation[]; syncing: boolean; onRefresh: () => void; onAudit: (a: AuditActivity) => void; }
type Filter = 'ALL' | 'DISCREPANCY' | 'UNAUDITED' | 'CONFIRMED';

export function AuditReportScreen({ audit, mine, syncing, onRefresh, onAudit }: Props) {
  const [filter, setFilter] = useState<Filter>('ALL');
  const [open, setOpen] = useState<string | null>(null);
  const s = audit?.summary;
  const rows = (audit?.activities ?? []).filter(r => filter === 'ALL' || r.audit_status === filter);
  const pendingMine = mine.filter(o => o.syncStatus === 'PENDING' || o.syncStatus === 'FAILED').length;

  return (
    <Screen>
      <Brand right={<Badge text="MANAGER" tone="orange" icon="shield" />} />
      <ScrollView contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 60 }} refreshControl={<RefreshControl refreshing={syncing} onRefresh={onRefresh} tintColor={C.amber} />}>
        <Text style={st.h1}>AUDIT REPORT</Text>
        <Mono style={{ marginTop: 6, fontSize: 12 }}>{audit ? `Generated ${audit.generated_at.slice(0, 16).replace('T', ' ')} UTC` : 'Pull down to generate'}</Mono>
        <View style={st.rule} />

        {pendingMine > 0 && <Button title={syncing ? 'Syncing...' : `Send ${pendingMine} pending audit${pendingMine > 1 ? 's' : ''}`} icon="upload-cloud" onPress={onRefresh} disabled={syncing} style={{ marginTop: 16 }} />}

        {s && (<>
          <View style={st.grid}>
            <Tile n={s.total_worker_claims} l="Worker reports" />
            <Tile n={s.total_audits} l="Manager audits" />
            <Tile n={`${Math.round(s.audit_coverage_pct)}%`} l="Audit coverage" tone={C.green} />
            <Tile n={s.discrepancies} l="Discrepancies" tone={s.discrepancies ? C.red : undefined} />
            <Tile n={s.confirmed} l="Confirmed" tone={C.green} />
            <Tile n={`${s.avg_over_reporting_pct}%`} l="Avg over-report" tone={s.avg_over_reporting_pct > 10 ? C.red : undefined} />
          </View>

          <Card style={{ marginTop: 16 }} accent={s.discrepancies ? C.red : C.green}>
            <Label>VERDICT</Label>
            <Text style={{ color: C.text, fontSize: 15, lineHeight: 22 }}>
              {s.activities_audited === 0
                ? 'No audits recorded yet. Visit the site and record what you verify against each worker claim.'
                : s.discrepancies === 0
                  ? `All ${s.activities_audited} audited activities match worker reports within tolerance.`
                  : `${s.discrepancies} of ${s.activities_audited} audited activities disagree with worker reports. Average over-reporting is ${s.avg_over_reporting_pct}%. Review the flagged items below before approving progress.`}
            </Text>
          </Card>
        </>)}

        <View style={st.filters}>
          {(['ALL', 'DISCREPANCY', 'UNAUDITED', 'CONFIRMED'] as Filter[]).map(f => (
            <TouchableOpacity key={f} onPress={() => setFilter(f)} style={[st.filter, filter === f && st.filterOn]}>
              <Text style={[st.filterText, filter === f && { color: C.onPrimary }]}>{f === 'ALL' ? 'All' : STATUS_META[f].text.replace('NOT AUDITED', 'To audit').replace(/^\w/, c => c)}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {rows.length === 0 && <Text style={{ color: C.muted, textAlign: 'center', marginTop: 30 }}>Nothing here.</Text>}
        {rows.map(r => {
          const m = STATUS_META[r.audit_status]; const ex = open === r.activity_id;
          return (
            <TouchableOpacity key={r.activity_id} activeOpacity={0.85} onPress={() => setOpen(ex ? null : r.activity_id)} style={st.row}>
              <View style={st.between}><Mono>{r.activity_id}</Mono><Badge text={m.text} tone={m.tone} icon={m.icon} /></View>
              <Text style={st.rowTitle}>{r.activity_name}</Text>
              <View style={[st.between, { marginTop: 10 }]}>
                <Cmp l="Claimed" v={claimText(r)} sub={r.latest_claim?.author} />
                <Icon name="arrow-right" size={16} color={C.muted} />
                <Cmp l="Verified" v={r.latest_audit ? `${r.audited_quantity ?? '—'} ${r.unit ?? ''}` : 'Not audited'} sub={r.latest_audit?.author} muted={!r.latest_audit} />
              </View>
              {r.variance_pct != null && (
                <View style={st.bar}><View style={[st.barFill, { width: `${Math.min(100, Math.abs(r.variance_pct))}%`, backgroundColor: Math.abs(r.variance_pct) > 10 ? C.red : C.green }]} />
                  <Text style={st.barText}>{r.variance_pct > 0 ? `${r.variance_pct}% over` : r.variance_pct < 0 ? `${-r.variance_pct}% under` : 'exact'}</Text></View>
              )}
              {ex && (
                <View style={st.detail}>
                  {r.reasons.map((x, i) => <View key={i} style={{ flexDirection: 'row', gap: 8, marginTop: 6 }}><Icon name="corner-down-right" size={14} color={C.muted} /><Text style={{ color: C.text, fontSize: 13, flex: 1, lineHeight: 19 }}>{x}</Text></View>)}
                  {r.latest_claim && <Text style={st.quote}>Worker: "{r.latest_claim.statement}"</Text>}
                  {r.latest_audit && <Text style={st.quote}>Manager: "{r.latest_audit.statement}"</Text>}
                  <Button title={r.latest_audit ? 'Re-audit this activity' : 'Audit this activity'} icon="clipboard" variant="outline" onPress={() => onAudit(r)} style={{ marginTop: 12, paddingVertical: 12 }} />
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </Screen>
  );
}

function Tile({ n, l, tone }: { n: number | string; l: string; tone?: string }) {
  return <View style={st.tile}><Text style={[st.tileN, tone ? { color: tone } : null]}>{n}</Text><Text style={st.tileL}>{l}</Text></View>;
}
function Cmp({ l, v, sub, muted }: { l: string; v: string; sub?: string | null; muted?: boolean }) {
  return <View style={{ flex: 1 }}><Label style={{ marginBottom: 2, fontSize: 10 }}>{l}</Label><Text style={{ color: muted ? C.muted : C.text, fontWeight: '600', fontSize: 14 }}>{v}</Text>{!!sub && <Mono style={{ fontSize: 11 }}>{sub}</Mono>}</View>;
}

const st = StyleSheet.create({
  h1: { color: C.text, fontSize: 28, fontWeight: '800', letterSpacing: 4, marginTop: 10 },
  rule: { height: 1, backgroundColor: C.border, marginTop: 14 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginTop: 18 },
  tile: { width: '31%', flexGrow: 1, backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: 6, padding: 12 },
  tileN: { color: C.text, fontSize: 22, fontWeight: '800' },
  tileL: { color: C.muted, fontSize: 11, marginTop: 4 },
  filters: { flexDirection: 'row', gap: 8, marginTop: 22, marginBottom: 6 },
  filter: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 6, borderWidth: 1, borderColor: C.border, backgroundColor: C.surface },
  filterOn: { backgroundColor: C.orange, borderColor: C.orange },
  filterText: { color: C.muted, fontSize: 12, fontWeight: '700' },
  row: { paddingVertical: 18, borderBottomWidth: 1, borderColor: C.border },
  between: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 10 },
  rowTitle: { color: C.text, fontSize: 17, fontWeight: '600', marginTop: 8 },
  bar: { height: 18, backgroundColor: C.surface2, borderRadius: 4, marginTop: 10, overflow: 'hidden', justifyContent: 'center' },
  barFill: { position: 'absolute', left: 0, top: 0, bottom: 0, opacity: 0.35 },
  barText: { color: C.text, fontSize: 11, fontWeight: '700', paddingHorizontal: 8 },
  detail: { marginTop: 12, paddingTop: 10, borderTopWidth: 1, borderColor: C.border },
  quote: { color: C.muted, fontSize: 12, fontStyle: 'italic', marginTop: 8 },
});
