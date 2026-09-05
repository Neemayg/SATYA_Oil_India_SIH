import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, RefreshControl } from 'react-native';
import { Screen, Brand, Icon, Label, Mono, Badge, Card } from '../components/ui';
import { C } from '../lib/theme';
import { Activity, Observation, Settings } from '../lib/types';

interface Props {
  settings: Settings; activities: Activity[]; observations: Observation[];
  online: boolean | null; lastSync: string | null; refreshing: boolean;
  onRefresh: () => void; onPickActivity: (a: Activity | null) => void;
}

function greeting() { const h = new Date().getHours(); return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'; }
function fmt(d?: string | null) { if (!d) return ''; const x = new Date(d); return isNaN(+x) ? d : x.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }).toUpperCase(); }
function ago(iso: string | null) { if (!iso) return 'never'; const m = Math.round((Date.now() - +new Date(iso)) / 60000); return m < 1 ? 'just now' : m < 60 ? `${m} min ago` : `${Math.round(m / 60)} h ago`; }

export function activityStatus(a: Activity, obs: Observation[]) {
  const mine = obs.filter(o => o.activityId === a.activity_id);
  if (mine.some(o => o.type === 'COMPLETION')) return { text: 'COMPLETE', tone: 'green' as const };
  if (mine.some(o => o.type === 'ISSUE')) return { text: 'ISSUE', tone: 'red' as const };
  if (mine.length) return { text: 'IN PROGRESS', tone: 'amber' as const };
  return { text: 'NOT STARTED', tone: 'muted' as const };
}

export function TodayScreen({ settings, activities, observations, online, lastSync, refreshing, onRefresh, onPickActivity }: Props) {
  const today = new Date();
  const list = [...activities].sort((a, b) => (b.is_critical ? 1 : 0) - (a.is_critical ? 1 : 0)).slice(0, 12);
  return (
    <Screen>
      <Brand right={<Icon name="bell" size={20} color={C.muted} />} />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 110 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={C.amber} />}>
        <Text style={s.hello}>{greeting()}, {settings.name || 'Engineer'}</Text>
        <Text style={s.sub}>{settings.crew} · Today, {fmt(today.toISOString())}</Text>
        <View style={s.syncPill}>
          <Icon name={online ? 'wifi' : online === false ? 'wifi-off' : 'loader'} size={14} color={online ? C.green : online === false ? C.red : C.muted} />
          <Text style={s.syncText}>{online ? `Synced · ${ago(lastSync)}` : online === false ? 'Offline · saving locally' : 'Checking...'}</Text>
        </View>

        <View style={s.secRow}>
          <Label style={{ marginBottom: 0 }}>TODAY'S ACTIVITIES</Label>
          <View style={s.count}><Text style={{ color: C.text, fontWeight: '700' }}>{list.length}</Text></View>
        </View>

        {list.length === 0 && (
          <Card>
            <Text style={{ color: C.text, fontWeight: '600' }}>No schedule activities loaded</Text>
            <Text style={{ color: C.muted, marginTop: 6, fontSize: 13 }}>Pull down to fetch from SATYA, or log an observation without an activity and the server will match it.</Text>
          </Card>
        )}
        {list.map((a, i) => {
          const st = activityStatus(a, observations);
          return (
            <TouchableOpacity key={a.activity_id} activeOpacity={0.85} onPress={() => onPickActivity(a)}>
              <Card style={{ marginBottom: 12 }} accent={i === 0 ? C.amber : undefined}>
                <View style={s.row}>
                  <Mono>{a.activity_id}</Mono>
                  <Badge text={st.text} tone={st.tone} />
                </View>
                <Text style={s.actName}>{a.activity_name}</Text>
                <View style={[s.row, { marginTop: 12 }]}>
                  <Mono style={{ fontSize: 12 }}>{a.wbs_code || 'WBS'} · {a.discipline}</Mono>
                  <Mono style={{ fontSize: 12 }}>{fmt(a.planned_start)}{a.planned_finish ? ` – ${fmt(a.planned_finish)}` : ''}</Mono>
                </View>
              </Card>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
      <TouchableOpacity style={s.fab} activeOpacity={0.85} onPress={() => onPickActivity(null)}>
        <Icon name="plus" size={18} color={C.onPrimary} /><Text style={s.fabText}>Log Field Observation</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const s = StyleSheet.create({
  hello: { color: C.text, fontSize: 26, fontWeight: '700', marginTop: 6 },
  sub: { color: C.muted, marginTop: 4, fontSize: 14 },
  syncPill: { flexDirection: 'row', alignItems: 'center', gap: 8, alignSelf: 'flex-start', marginTop: 16, paddingHorizontal: 14, paddingVertical: 10, backgroundColor: C.surface, borderWidth: 1, borderColor: C.border, borderRadius: 6 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  syncText: { color: C.text, fontSize: 14 },
  secRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 30, marginBottom: 14 },
  count: { borderWidth: 1, borderColor: C.border, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 4 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  actName: { color: C.text, fontSize: 20, fontWeight: '600', marginTop: 14 },
  fab: { position: 'absolute', right: 20, bottom: 20, flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: C.orange, paddingHorizontal: 20, paddingVertical: 16, borderRadius: 8, elevation: 4, shadowColor: '#000', shadowOpacity: 0.15, shadowRadius: 6, shadowOffset: { width: 0, height: 3 } },
  fabText: { color: C.onPrimary, fontWeight: '800', fontSize: 15 },
});
