import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Alert, RefreshControl } from 'react-native';
import { Screen, Brand, Icon, IconButton, Label, Mono, Badge, Card, Button, Tone } from '../components/ui';
import { C } from '../lib/theme';
import { Observation, TYPE_LABEL } from '../lib/types';
import { buildStatement } from '../lib/api';

interface Props {
  items: Observation[]; banner: Observation | null; syncing: boolean;
  onDismissBanner: () => void; onSync: () => void; onDelete: (id: string) => void; onSubmitDraft: (id: string) => void;
}

function badgeFor(o: Observation): { text: string; tone: Tone } {
  if (o.syncStatus === 'DRAFT') return { text: 'Draft', tone: 'muted' };
  if (o.syncStatus === 'FAILED') return { text: 'Sync failed', tone: 'red' };
  if (o.syncStatus === 'PENDING') return { text: 'Waiting to sync', tone: 'amber' };
  if (o.trustStatus === 'TRUSTED') return { text: 'Trusted', tone: 'green' };
  if (o.trustStatus === 'REVIEW_REQUIRED' || o.matchOutcome === 'AMBIGUOUS' || o.matchOutcome === 'INSUFFICIENT_EVIDENCE') return { text: 'Needs review', tone: 'orange' };
  if (o.matchOutcome === 'UNMATCHED') return { text: 'Unmatched', tone: 'red' };
  if (o.matchOutcome === 'MATCHED') return { text: 'Matched', tone: 'green' };
  return { text: 'Extracted', tone: 'green' };
}
function when(iso: string) {
  const d = new Date(iso), now = new Date();
  const days = Math.floor((+now.setHours(0, 0, 0, 0) - +new Date(d).setHours(0, 0, 0, 0)) / 86400000);
  const t = d.toTimeString().slice(0, 5);
  return days === 0 ? `Today · ${t}` : days === 1 ? `Yesterday · ${t}` : days < 7 ? `${days} days ago · ${t}` : d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
}

export function ReportsScreen({ items, banner, syncing, onDismissBanner, onSync, onDelete, onSubmitDraft }: Props) {
  const [open, setOpen] = useState<string | null>(null);
  const sorted = [...items].sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  const weekAgo = Date.now() - 7 * 86400000;
  const thisWeek = sorted.filter(o => +new Date(o.createdAt) >= weekAgo);
  const earlier = sorted.filter(o => +new Date(o.createdAt) < weekAgo);
  const pending = items.filter(o => o.syncStatus === 'PENDING' || o.syncStatus === 'FAILED').length;

  const Row = ({ o }: { o: Observation }) => {
    const b = badgeFor(o); const ex = open === o.id;
    return (
      <TouchableOpacity activeOpacity={0.85} onPress={() => setOpen(ex ? null : o.id)} style={s.row}>
        <View style={s.between}>
          <Mono>{o.activityId || o.serverSourceId || o.id}</Mono>
          <Mono style={{ fontSize: 12 }}>{when(o.createdAt)}</Mono>
        </View>
        <Text style={s.rowTitle}>{TYPE_LABEL[o.type]} — {o.activityName || o.note || `${o.discipline} work`}</Text>
        <View style={{ flexDirection: 'row', gap: 8, marginTop: 12, alignItems: 'center' }}>
          <Badge text={b.text} tone={b.tone} filled />
          {o.matchConfidence != null && <Mono style={{ fontSize: 12 }}>{Math.round(o.matchConfidence * 100)}% match</Mono>}
          {o.photoUri && <Icon name="camera" size={14} color={C.muted} />}
          {o.audioUri && <Icon name="mic" size={14} color={C.muted} />}
        </View>
        {ex && (
          <View style={s.detail}>
            <D k="Sent as" v={buildStatement(o)} />
            {o.area ? <D k="Area" v={o.area} /> : null}
            {o.serverSourceId && <D k="Source" v={o.serverSourceId} />}
            {o.serverEventIds?.length ? <D k="Events" v={o.serverEventIds.join(', ')} /> : null}
            {o.matchOutcome && <D k="Match" v={`${o.matchOutcome}${o.matchActivityId ? ` → ${o.matchActivityId}` : ''}`} />}
            {o.trustStatus && <D k="Trust" v={o.trustStatus} />}
            {o.syncError && <D k="Error" v={o.syncError} red />}
            <View style={{ flexDirection: 'row', gap: 10, marginTop: 14 }}>
              {o.syncStatus === 'DRAFT' && <Button title="Submit" onPress={() => onSubmitDraft(o.id)} style={{ flex: 1, paddingVertical: 12 }} />}
              {o.syncStatus !== 'SYNCED' && <Button title="Delete" variant="danger" style={{ flex: 1, paddingVertical: 12 }}
                onPress={() => Alert.alert('Delete this observation?', 'It has not reached the server.', [{ text: 'Keep' }, { text: 'Delete', style: 'destructive', onPress: () => onDelete(o.id) }])} />}
            </View>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <Screen>
      <Brand />
      <ScrollView contentContainerStyle={{ paddingHorizontal: 20, paddingBottom: 100 }} refreshControl={<RefreshControl refreshing={syncing} onRefresh={onSync} tintColor={C.amber} />}>
        <Text style={s.h1}>MY REPORTS</Text>
        <View style={s.rule} />
        {banner && (
          <Card accent={C.green} style={{ marginTop: 20, flexDirection: 'row', gap: 12 }}>
            <Icon name="check-circle" size={22} color={C.green} />
            <View style={{ flex: 1 }}>
              <Text style={{ color: C.text, fontSize: 16, fontWeight: '600' }}>
                Observation {banner.syncStatus === 'SYNCED' ? 'submitted' : 'saved'} — {banner.serverSourceId || banner.id}{banner.activityId ? ` · ${banner.activityId}` : ''}
              </Text>
              <Text style={{ color: C.muted, marginTop: 4, fontSize: 13 }}>
                {banner.syncStatus === 'SYNCED' ? 'Extraction and matching complete. Pull down to refresh trust status.' : 'Saved on this device. It will be sent when you sync.'}
              </Text>
            </View>
            <IconButton name="x" color={C.muted} size={18} onPress={onDismissBanner} />
          </Card>
        )}
        {pending > 0 && <Button title={syncing ? 'Syncing...' : `Sync ${pending} pending`} onPress={onSync} disabled={syncing} style={{ marginTop: 20 }} />}

        {items.length === 0 && <Text style={{ color: C.muted, marginTop: 40, textAlign: 'center' }}>No reports yet. Log an observation from Today or Capture.</Text>}
        {thisWeek.length > 0 && <Label style={{ marginTop: 30 }}>THIS WEEK</Label>}
        {thisWeek.map(o => <Row key={o.id} o={o} />)}
        {earlier.length > 0 && <Label style={{ marginTop: 30 }}>EARLIER</Label>}
        {earlier.map(o => <Row key={o.id} o={o} />)}
      </ScrollView>
    </Screen>
  );
}

function D({ k, v, red }: { k: string; v: string; red?: boolean }) {
  return (
    <View style={{ flexDirection: 'row', gap: 12, marginTop: 8 }}>
      <Mono style={{ width: 64, fontSize: 12 }}>{k}</Mono>
      <Text style={{ color: red ? C.red : C.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{v}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  h1: { color: C.text, fontSize: 28, fontWeight: '800', letterSpacing: 4, marginTop: 10 },
  rule: { height: 1, backgroundColor: C.border, marginTop: 18 },
  row: { paddingVertical: 20, borderBottomWidth: 1, borderColor: C.border },
  between: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  rowTitle: { color: C.text, fontSize: 18, fontWeight: '500', marginTop: 10, lineHeight: 26 },
  detail: { marginTop: 14, paddingTop: 12, borderTopWidth: 1, borderColor: C.border },
});
