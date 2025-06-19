import 'package:flutter/material.dart';
import 'package:plate_recognition/screens/homescreen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Plate Recognition App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        textTheme: Theme.of(context).textTheme.apply(fontFamily: 'Poppins'),
      ),
      home:
          const HomeScreenStyled(), // Ganti ke `HomeScreen()` jika ingin lihat versi awal
    );
  }
}
