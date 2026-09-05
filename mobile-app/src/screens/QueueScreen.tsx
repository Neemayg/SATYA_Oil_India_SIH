import React from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { C } from '../lib/theme';
import { Observation } from '../lib/types';
import { buildStatement } from '../lib/api';

interface Props { items: Observation[]; syncing: boolean; onSync: () => void; onDelete: (id: string) => void; }

const COLOR = { PENDING: C.accent, SYNCED: C.green, FAILED: C.red };

export function QueueScreen({ items, syncing, onSync, onDelete }: Props) {
  const pending = items.filter(i => i.syncStatus !== 'SYNCED').length;
  return (
    <View style={s.root}>
      <View style={s.header}>
        <View>
          <Text style={s.h1}>Sync Queue</Text>
          <Text style={s.sub}>{pending} pending · {items.length - pending} synced</Text>
        </View>
        <TouchableOpacity style={[s.syncBtn, (syncing || pending === 0) && { opacity: 0.5 }]} disabled={syncing || pending === 0} onPress={onSync}>
          <Text style={s.syncText}>{syncing ? 'Syncing...' : 'Sync now'}</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={[...items].reverse()}
        keyExtractor={i => i.id}
        contentContainerStyle={{ padding: 16, gap: 10 }}
        ListEmptyComponent={<Text style={s.empty}>No observations yet. Capture one from the Log tab.</Text>}
        renderItem={({ item }) => (
          <TouchableOpacity style={s.card} onLongPress={() => Alert.alert('Delete observation?', item.id, [
            { text: 'Cancel' }, { text: 'Delete', style: 'destructive', onPress: () => onDelete(item.id) }])}>
            <View style={s.row}>
              <Text style={s.type}>{item.type} · {item.discipline}</Text>
              <Text style={[s.badge, { color: COLOR[item.syncStatus] }]}>● {item.syncStatus}</Text>
            </View>
            <Text style={s.stmt}>{buildStatement(item)}</Text>
            <Text style={s.meta}>
              {item.observedAt}{item.photoUri ? ' · photo' : ''}{item.audioUri ? ' · voice' : ''}
              {item.serverSourceId ? ` · ${item.serverSourceId}` : ''}
              {item.eventsExtracted != null ? ` · ${item.eventsExtracted} event(s) extracted` : ''}
            </Text>
            {item.syncError && <Text style={s.err}>{item.syncError}</Text>}
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderColor: C.border },
  h1: { color: C.text, fontSize: 22, fontWeight: '700', letterSpacing: 1 },
  sub: { color: C.muted, fontSize: 12 },
  syncBtn: { backgroundColor: C.accent, paddingHorizontal: 16, paddingVertical: 10, borderRadius: 8 },
  syncText: { color: '#000', fontWeight: '800' },
  card: { backgroundColor: C.card, borderWidth: 1, borderColor: C.border, borderRadius: 10, padding: 12 },
  row: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  type: { color: C.accent, fontSize: 11, fontWeight: '700', letterSpacing: 1 },
  badge: { fontSize: 11, fontWeight: '700' },
  stmt: { color: C.text, fontSize: 14, lineHeight: 20 },
  meta: { color: C.muted, fontSize: 11, marginTop: 6 },
  err: { color: C.red, fontSize: 11, marginTop: 4 },
  empty: { color: C.muted, textAlign: 'center', marginTop: 60 },
});
