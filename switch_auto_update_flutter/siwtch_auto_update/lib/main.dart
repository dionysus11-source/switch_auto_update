import 'dart:io';
import 'package:flutter/material.dart';
import 'dart:async';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Switch Auto updater',
      theme: ThemeData(
          // This is the theme of your application.
          //
          // Try running your application with "flutter run". You'll see the
          // application has a blue toolbar. Then, without quitting the app, try
          // changing the primarySwatch below to Colors.green and then invoke
          // "hot reload" (press "r" in the console where you ran "flutter run",
          // or simply save your changes to "hot reload" in a Flutter IDE).
          // Notice that the counter didn't reset back to zero; the application
          // is not restarted.
          primarySwatch: Colors.deepOrange),
      home: MediaQuery(
        data: const MediaQueryData(
          size: Size(600, 800),
        ),
        child: UsbCopyApp(),
      ),
    );
  }
}

class UsbCopyApp extends StatefulWidget {
  @override
  _UsbCopyAppState createState() => _UsbCopyAppState();
}

class _UsbCopyAppState extends State<UsbCopyApp> {
  List<String> _usbDrivePaths = List.filled(0, "");
  String _selectedDrivePath = "";
  double _copyProgress = 0;
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      _usbDrivePaths = await _getUsbDrivePaths();
      if (_usbDrivePaths.isNotEmpty) {
        setState(() {});
      }
    });
  }

  Future<void> _checkUsb() async {
    _usbDrivePaths = await _getUsbDrivePaths();
    if (_usbDrivePaths.isNotEmpty) {
      setState(() {});
    }
  }

  Future<List<String>> _getUsbDrivePaths() async {
    final usbDrives = <String>[];
    await Directory('/')
        .list(recursive: true, followLinks: false)
        .forEach((drive) async {
      try {
        if (drive.path.startsWith("/media/") ||
            drive.path.startsWith("/Volumes/") &&
                !drive.path.contains("\$Recycle.Bin") &&
                !drive.path.contains("System Volume Information")) {
          usbDrives.add(drive.path);
        }
      } catch (e) {
        print("An error occurred: $e");
      }
    });
    return usbDrives;
  }

  Future<void> _copyFolderToUsb() async {
    if (_selectedDrivePath == "") {
      return;
    }
    setState(() {
      _copyProgress = 0;
    });
    final Directory folderToCopy = Directory('./Download');
    if (!folderToCopy.existsSync()) {
      folderToCopy.createSync();
    }
    final Directory copiedFolder = Directory('$_selectedDrivePath/');
    final Stream<FileSystemEntity> entityList =
        folderToCopy.list(recursive: true, followLinks: false);
    final int entityCount = await entityList.length;
    int copiedCount = 0;

    await entityList.forEach((FileSystemEntity entity) async {
      final String newPath =
          entity.path.replaceFirst(folderToCopy.path, copiedFolder.path);
      if (entity is File) {
        await File(entity.path).copy(newPath);
      } else if (entity is Directory) {
        await Directory(newPath).create(recursive: true);
      }
      copiedCount++;
      setState(() {
        _copyProgress = copiedCount / entityCount;
      });
    });

    setState(() {
      _copyProgress = 1;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Switch Auto Updater'),
      ),
      body: Column(
        children: [
          if (_usbDrivePaths == null)
            const CircularProgressIndicator()
          else if (_usbDrivePaths.isEmpty)
            const Text(
              'No USB drive detected',
              style: TextStyle(
                fontSize: 15,
              ),
            )
          else
            Expanded(
              child: ListView.builder(
                itemCount: _usbDrivePaths.length,
                itemBuilder: (BuildContext context, int index) {
                  return ListTile(
                    title: Text(_usbDrivePaths[index]),
                    onTap: () {
                      setState(() {
                        _selectedDrivePath = _usbDrivePaths[index];
                      });
                    },
                    selected: _selectedDrivePath == _usbDrivePaths[index],
                  );
                },
              ),
            ),
          if (_selectedDrivePath != null)
            Column(
              children: [
                LinearProgressIndicator(
                  value: _copyProgress,
                ),
                if (_copyProgress < 1)
                  ElevatedButton(
                    onPressed: _checkUsb,
                    child: const Text(
                      'Refresh USB Drive List',
                      style: TextStyle(
                        fontSize: 20,
                      ),
                    ),
                  )
                else if (_copyProgress == 100)
                  const Text('Copy complete'),
              ],
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color.fromRGBO(254, 110, 14, 1),
        onPressed: _copyFolderToUsb,
        child: const Icon(
          Icons.content_copy,
        ),
      ),
    );
  }
}
