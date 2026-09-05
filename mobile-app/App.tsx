import React, { useEffect, useState, useCallback, useRef } from 'react';
import { SafeAreaView, StatusBar as RNStatusBar, Platform, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SignInScreen } from './src/screens/SignInScreen';
import { TodayScreen } from './src/screens/TodayScreen';
import { AuditTodayScreen } from './src/screens/AuditTodayScreen';
import { CaptureScreen } from './src/screens/CaptureScreen';
import { ReportsScreen } from './src/screens/ReportsScreen';
import { AuditReportScreen } from './src/screens/AuditReportScreen';
import { ProfileScreen } from './src/screens/ProfileScreen';
import { TabBar } from './src/components/ui';
import { C } from './src/lib/theme';
import { Activity, AuditActivity, AuditReport, Observation, Settings } from './src/lib/types';
import { loadObservations, saveObservations, loadSettings, saveSettings, loadActivities, saveActivities, DEFAULT_SETTINGS } from './src/lib/storage';
import { uploadObservation, checkHealth, fetchActivities, fetchEventStatus, fetchAudit } from './src/lib/api';

type Tab = 'today' | 'capture' | 'reports' | 'profile';

export default function App() {
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<Tab>('today');
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [items, setItems] = useState<Observation[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [audit, setAudit] = useState<AuditReport | null>(null);
  const [online, setOnline] = useState<boolean | null>(null);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [captureActivity, setCaptureActivity] = useState<Activity | null>(null);
  const [captureClaim, setCaptureClaim] = useState<AuditActivity | null>(null);
  const [captureKey, setCaptureKey] = useState(0);
  const [banner, setBanner] = useState<Observation | null>(null);
  const itemsRef = useRef(items); itemsRef.current = items;
  const isManager = settings.role === 'MANAGER';

  useEffect(() => {
    (async () => {
      const [obs, st, acts] = await Promise.all([loadObservations(), loadSettings(), loadActivities()]);
      setItems(obs); setSettings(st); setActivities(acts); setReady(true);
      if (st.signedIn) refresh(st);
    })();
  }, []);

  const persist = useCallback((next: Observation[]) => { setItems(next); itemsRef.current = next; saveObservations(next); }, []);
  const updateSettings = (s: Settings) => { setSettings(s); saveSettings(s); };

  async function refresh(st = settings) {
    setRefreshing(true);
    const ok = await checkHealth(st);
    setOnline(ok);
    if (ok) {
      try { const acts = await fetchActivities(st); if (acts.length) { setActivities(acts); saveActivities(acts); } } catch {}
      await syncPending(st, false);
      try { setAudit(await fetchAudit(st)); } catch {}
      setLastSync(new Date().toISOString());
    }
    setRefreshing(false);
  }

  async function syncPending(st = settings, showBanner = true) {
    setSyncing(true);
    let cur = [...itemsRef.current];
    let last: Observation | null = null;
    for (const o of cur) {
      if (o.syncStatus === 'PENDING' || o.syncStatus === 'FAILED') {
        try {
          const r = await uploadObservation(o, st);
          const upd: Observation = { ...o, syncStatus: 'SYNCED', syncError: undefined, serverSourceId: r.sourceId, serverEventIds: r.eventIds };
          cur = cur.map(i => i.id === o.id ? upd : i); last = upd;
        } catch (e: any) {
          cur = cur.map(i => i.id === o.id ? { ...i, syncStatus: 'FAILED', syncError: String(e?.message ?? e) } : i);
        }
        persist(cur);
      }
    }
    for (const o of cur) {
      if (o.syncStatus === 'SYNCED' && o.serverEventIds?.[0] && !o.trustStatus) {
        const extra = await fetchEventStatus(o.serverEventIds[0], st);
        if (Object.keys(extra).length) cur = cur.map(i => i.id === o.id ? { ...i, ...extra } : i);
      }
    }
    persist(cur);
    if (showBanner && last) setBanner(last);
    setSyncing(false);
    setLastSync(new Date().toISOString());
  }

  async function onSubmit(o: Observation, draft: boolean) {
    persist([...itemsRef.current, o]);
    setTab('reports');
    setBanner(o);
    if (!draft && online !== false) {
      const ok = await checkHealth(settings); setOnline(ok);
      if (ok) { await syncPending(settings, true); try { setAudit(await fetchAudit(settings)); } catch {} }
    }
  }

  function openCapture(a: Activity | null, claim: AuditActivity | null = null) {
    setCaptureActivity(a); setCaptureClaim(claim); setCaptureKey(k => k + 1); setTab('capture');
  }
  function auditFromReport(r: AuditActivity) {
    const a = activities.find(x => x.activity_id === r.activity_id) ?? { activity_id: r.activity_id, activity_name: r.activity_name, discipline: r.discipline ?? 'CIVIL', unit_of_measure: r.unit, is_critical: r.is_critical };
    openCapture(a, r);
  }

  if (!ready) return <View style={{ flex: 1, backgroundColor: C.bg }} />;

  const pending = items.filter(i => i.syncStatus === 'PENDING' || i.syncStatus === 'FAILED').length;
  const wrap = (child: React.ReactNode) => (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.bg, paddingTop: Platform.OS === 'android' ? RNStatusBar.currentHeight : 0 }}>
      <StatusBar style="dark" />
      {child}
    </SafeAreaView>
  );

  if (!settings.signedIn) return wrap(<SignInScreen settings={settings} onSignIn={s => { updateSettings(s); refresh(s); }} />);

  return wrap(<>
    <View style={{ flex: 1 }}>
      {tab === 'today' && (isManager
        ? <AuditTodayScreen settings={settings} audit={audit} activities={activities} online={online} refreshing={refreshing} onRefresh={() => refresh()} onAudit={openCapture} />
        : <TodayScreen settings={settings} activities={activities} observations={items} online={online} lastSync={lastSync} refreshing={refreshing} onRefresh={() => refresh()} onPickActivity={a => openCapture(a)} />)}
      {tab === 'capture' && <CaptureScreen key={captureKey} settings={settings} activities={activities} initialActivity={captureActivity} claim={captureClaim} onSubmit={onSubmit} onBack={() => setTab('today')} />}
      {tab === 'reports' && (isManager
        ? <AuditReportScreen audit={audit} mine={items.filter(i => i.isAudit)} syncing={syncing || refreshing} onRefresh={() => refresh()} onAudit={auditFromReport} />
        : <ReportsScreen items={items} banner={banner} syncing={syncing} onDismissBanner={() => setBanner(null)} onSync={() => refresh()}
            onDelete={id => persist(itemsRef.current.filter(i => i.id !== id))}
            onSubmitDraft={id => { persist(itemsRef.current.map(i => i.id === id ? { ...i, syncStatus: 'PENDING' } : i)); syncPending(); }} />)}
      {tab === 'profile' && <ProfileScreen settings={settings} onChange={updateSettings} onSync={() => refresh()}
        stats={{ total: items.length, pending, synced: items.filter(i => i.syncStatus === 'SYNCED').length, activities: activities.length }}
        onSignOut={() => updateSettings({ ...settings, signedIn: false })} />}
    </View>
    <TabBar active={tab} badge={pending} onChange={(t: Tab) => t === 'capture' ? openCapture(null) : setTab(t)} />
  </>);
}
