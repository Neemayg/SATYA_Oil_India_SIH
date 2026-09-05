import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView, StatusBar as RNStatusBar, Platform } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { CaptureScreen } from './src/screens/CaptureScreen';
import { QueueScreen } from './src/screens/QueueScreen';
import { SettingsScreen } from './src/screens/SettingsScreen';
import { C } from './src/lib/theme';
import { Observation, Settings } from './src/lib/types';
import { loadObservations, saveObservations, loadSettings, saveSettings, DEFAULT_SETTINGS } from './src/lib/storage';
import { uploadObservation } from './src/lib/api';

type Tab = 'capture' | 'queue' | 'settings';

export default function App() {
  const [tab, setTab] = useState<Tab>('capture');
  const [items, setItems] = useState<Observation[]>([]);
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    loadObservations().then(setItems);
    loadSettings().then(setSettings);
  }, []);

  const persist = useCallback((next: Observation[]) => { setItems(next); saveObservations(next); }, []);

  function onSave(o: Observation) { persist([...items, o]); }
  function onDelete(id: string) { persist(items.filter(i => i.id !== id)); }
  function onSettings(s: Settings) { setSettings(s); saveSettings(s); }

  async function sync() {
    setSyncing(true);
    let current = [...items];
    for (const o of current) {
      if (o.syncStatus === 'SYNCED') continue;
      try {
        const r = await uploadObservation(o, settings);
        current = current.map(i => i.id === o.id ? { ...i, syncStatus: 'SYNCED', syncError: undefined, serverSourceId: r.sourceId, eventsExtracted: r.eventsExtracted } : i);
      } catch (e: any) {
        current = current.map(i => i.id === o.id ? { ...i, syncStatus: 'FAILED', syncError: String(e?.message ?? e) } : i);
      }
      persist(current);
    }
    setSyncing(false);
  }

  const pending = items.filter(i => i.syncStatus !== 'SYNCED').length;

  return (
    <SafeAreaView style={s.root}>
      <StatusBar style="light" />
      <View style={s.top}>
        <Text style={s.brand}>SATYA</Text>
        <Text style={s.brandSub}>FIELD CAPTURE</Text>
      </View>
      <View style={{ flex: 1 }}>
        {tab === 'capture' && <CaptureScreen settings={settings} onSave={onSave} />}
        {tab === 'queue' && <QueueScreen items={items} syncing={syncing} onSync={sync} onDelete={onDelete} />}
        {tab === 'settings' && <SettingsScreen settings={settings} onChange={onSettings} />}
      </View>
      <View style={s.tabs}>
        <TabBtn label="Log" active={tab === 'capture'} onPress={() => setTab('capture')} />
        <TabBtn label="Queue" badge={pending} active={tab === 'queue'} onPress={() => setTab('queue')} />
        <TabBtn label="Settings" active={tab === 'settings'} onPress={() => setTab('settings')} />
      </View>
    </SafeAreaView>
  );
}

function TabBtn({ label, active, badge, onPress }: { label: string; active: boolean; badge?: number; onPress: () => void }) {
  return (
    <TouchableOpacity style={s.tab} onPress={onPress}>
      <Text style={[s.tabLabel, active && { color: C.accent }]}>{label}{badge ? ` (${badge})` : ''}</Text>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg, paddingTop: Platform.OS === 'android' ? RNStatusBar.currentHeight : 0 },
  top: { flexDirection: 'row', alignItems: 'baseline', gap: 8, paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderColor: C.border },
  brand: { color: C.accent, fontSize: 20, fontWeight: '900', letterSpacing: 3 },
  brandSub: { color: C.muted, fontSize: 11, letterSpacing: 2 },
  tabs: { flexDirection: 'row', borderTopWidth: 1, borderColor: C.border, backgroundColor: C.card },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 14 },
  tabLabel: { color: C.muted, fontSize: 14, fontWeight: '700' },
});
