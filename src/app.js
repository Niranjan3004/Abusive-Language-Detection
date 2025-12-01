import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  StatusBar,
  Dimensions,
  Platform
} from "react-native";
import { MaterialIcons, Entypo } from "@expo/vector-icons";
import { StatusBar as ExpoStatusBar } from "expo-status-bar";

const { width } = Dimensions.get("window");

const MOCK_BOOKINGS = [
  {
    id: "TICKET-001",
    from: "SOLAPUR",
    to: "PUNE JN.",
    fare: "₹115.00",
    travelClass: "SECOND (II)",
    service: "SUPERFAST (S)",
    adults: 1,
    children: 0,
    bookingDate: "NOV 16, 2025 05:38:52"   // ✅ UPDATED DATE
  },
  {
    id: "TICKET-002",
    from: "PUNE JN.",
    to: "SOLAPUR",
    fare: "₹115.00",
    travelClass: "SECOND (II)",
    service: "SUPERFAST (S)",
    adults: 1,
    children: 0,
    bookingDate: "NOV 02, 2025 08:00:45"
  }
];

function BookingCard({ item }) {
  return (
    <View style={styles.cardWrap}>
      <View style={styles.cardInner}>

        {/* Header Row */}
        <View style={styles.headerRow}>
          <View style={styles.journeyBox}>
            <Text style={styles.journeyLabel}>JOURNEY ( M-TICKET )</Text>
          </View>
          <View style={styles.fareBox}>
            <Text style={styles.fareLabel}>FARE:</Text>
            <Text style={styles.fareAmount}>{item.fare}</Text>
          </View>
        </View>

        {/* Route */}
        <View style={styles.routeRow}>
          <View style={styles.stationCol}>
            <View style={styles.stationRow}>
              <View style={styles.stationIconS}>
                <Text style={styles.stationIconText}>S</Text>
              </View>
              <Text style={styles.stationText}>{item.from}</Text>
            </View>
          </View>

          <View style={styles.stationCol}>
            <View style={styles.stationRow}>
              <View style={styles.stationIconD}>
                <Text style={styles.stationIconText}>D</Text>
              </View>
              <Text style={styles.stationText}>{item.to}</Text>
            </View>
          </View>
        </View>

        {/* Paperless Stamp */}
        <View style={styles.stampWrap}>
          <View style={styles.stampCircle}>
            <Text style={styles.stampText}>PAPERLESS</Text>
          </View>
        </View>

        {/* Via Row */}
        <Text style={styles.infoText}>Via:</Text>

        {/* Details */}
        <View style={styles.detailsRow}>
          <View>
            <Text style={styles.smallBold}>
              ADULT: <Text style={styles.smallNormal}>{item.adults}</Text>  CHILD:{" "}
              <Text style={styles.smallNormal}>{item.children}</Text>
            </Text>

            <Text style={styles.smallNormal}>
              {item.travelClass}     {item.service}
            </Text>
          </View>

          <View style={{ alignItems: "flex-end" }}>
            <Text style={styles.bookingDateLabel}>BOOKING DATE:</Text>
            <Text style={styles.bookingDateVal}>{item.bookingDate}</Text>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.actionsRow}>
          <TouchableOpacity style={styles.actionLeft}>
            <Entypo name="arrow-long-left" size={18} color="#ff6b6b" />
            <Text style={styles.actionText}>BOOK AGAIN</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionRight}>
            <MaterialIcons name="search" size={18} color="#ff6b6b" />
            <Text style={styles.actionText}>NEXT TRAINS</Text>
          </TouchableOpacity>
        </View>

      </View>
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaView style={styles.safe}>
      <ExpoStatusBar style="dark" />
      <StatusBar barStyle="light-content" backgroundColor="#ff8a65" />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.back}>
          <MaterialIcons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>

        <Text style={styles.headerTitle}>Booking History</Text>

        <TouchableOpacity style={styles.refresh}>
          <MaterialIcons name="refresh" size={22} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Big Button */}
      <View style={styles.bigButtonRow}>
        <View style={styles.bigCTA}>
          <Entypo name="ticket" size={18} color="#fff" />
          <Text style={styles.ctaText}>BOOKING HISTORY</Text>
        </View>
      </View>

      {/* List */}
      <FlatList
        data={MOCK_BOOKINGS}
        keyExtractor={(i) => i.id}
        renderItem={({ item }) => <BookingCard item={item} />}
        contentContainerStyle={{ paddingBottom: 100 }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#fff" },

  header: {
    height: Platform.OS === "android" ? 60 : 88,
    backgroundColor: "#ff8a65",
    paddingTop: Platform.OS === "android" ? 18 : 36,
    paddingHorizontal: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  back: { position: "absolute", left: 12 },
  refresh: { position: "absolute", right: 12 },
  headerTitle: { color: "#fff", fontSize: 18, fontWeight: "700" },

  bigButtonRow: { padding: 10 },
  bigCTA: {
    backgroundColor: "#ff8a65",
    padding: 12,
    borderRadius: 8,
    flexDirection: "row",
    justifyContent: "center",
    gap: 10,
  },
  ctaText: { color: "#fff", fontSize: 15, fontWeight: "700" },

  cardWrap: {
    margin: 10,
    borderRadius: 12,
    backgroundColor: "#fff",
    elevation: 5,
  },
  cardInner: { padding: 15 },

  headerRow: { flexDirection: "row" },
  journeyBox: {
    backgroundColor: "#dff7fb",
    padding: 8,
    borderRadius: 6,
    flex: 1,
  },
  journeyLabel: { fontWeight: "700", color: "#1a5366" },
  fareBox: {
    backgroundColor: "#c7f0ff",
    padding: 8,
    borderRadius: 6,
    marginLeft: 10,
  },
  fareLabel: { fontSize: 12, fontWeight: "700", color: "#1a5366" },
  fareAmount: { fontSize: 17, fontWeight: "800", color: "#0b3b3f" },

  routeRow: { flexDirection: "row", marginTop: 12 },

  stationCol: { flex: 1 },
  stationRow: { flexDirection: "row", alignItems: "center" },
  stationIconS: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: "#ffcc80", alignItems: "center", justifyContent: "center",
    marginRight: 8,
  },
  stationIconD: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: "#ff8a80", alignItems: "center", justifyContent: "center",
    marginRight: 8,
  },
  stationIconText: { color: "#fff", fontWeight: "700" },
  stationText: { fontSize: 17, fontWeight: "800" },

  stampWrap: {
    position: "absolute",
    top: 95,
    left: width / 2 - 40,
    opacity: 0.13,
  },
  stampCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: "#57b37c",
    alignItems: "center",
    justifyContent: "center",
    transform: [{ rotate: "-10deg" }],
  },
  stampText: { color: "#57b37c", fontWeight: "900" },

  infoText: { marginTop: 20, color: "#666" },

  detailsRow: {
    marginTop: 6,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  smallBold: { fontWeight: "700", color: "#333" },
  smallNormal: { fontWeight: "600", color: "#666" },
  bookingDateLabel: { fontWeight: "700", color: "#ff8a65" },
  bookingDateVal: { color: "#d35400", marginTop: 2 },

  actionsRow: {
    marginTop: 14,
    paddingTop: 10,
    borderTopWidth: 1,
    borderColor: "#eee",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  actionText: { color: "#ff6b6b", fontWeight: "700" },
});
