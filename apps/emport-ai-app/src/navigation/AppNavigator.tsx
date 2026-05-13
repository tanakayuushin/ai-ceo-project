import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';

import HomeScreen from '../screens/HomeScreen';
import ChatScreen from '../screens/ChatScreen';
import SubsidyScreen from '../screens/SubsidyScreen';
import MemoScreen from '../screens/MemoScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Tab = createBottomTabNavigator();

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ focused, color, size }) => {
            const icons: Record<string, [string, string]> = {
              Home: ['home', 'home-outline'],
              Chat: ['chatbubbles', 'chatbubbles-outline'],
              Subsidy: ['cash', 'cash-outline'],
              Memo: ['document-text', 'document-text-outline'],
              Settings: ['settings', 'settings-outline'],
            };
            const [active, inactive] = icons[route.name] || ['help', 'help-outline'];
            return <Ionicons name={(focused ? active : inactive) as any} size={size} color={color} />;
          },
          tabBarActiveTintColor: Colors.accent,
          tabBarInactiveTintColor: Colors.textMuted,
          tabBarStyle: {
            backgroundColor: Colors.surface,
            borderTopColor: Colors.border,
            borderTopWidth: 1,
            height: 65,
            paddingBottom: 10,
          },
          tabBarLabelStyle: { fontSize: 10, fontWeight: '600' },
        })}
      >
        <Tab.Screen name="Home" component={HomeScreen} options={{ tabBarLabel: 'ホーム' }} />
        <Tab.Screen name="Chat" component={ChatScreen} options={{ tabBarLabel: 'AI相談' }} />
        <Tab.Screen name="Subsidy" component={SubsidyScreen} options={{ tabBarLabel: '補助金' }} />
        <Tab.Screen name="Memo" component={MemoScreen} options={{ tabBarLabel: 'メモ' }} />
        <Tab.Screen name="Settings" component={SettingsScreen} options={{ tabBarLabel: '設定' }} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
