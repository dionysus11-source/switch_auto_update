import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:archive/archive_io.dart';
import 'package:path/path.dart' as path;
import 'package:flutter_archive/flutter_archive.dart';

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
    /*
    _timer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      _usbDrivePaths = await _getUsbDrivePaths();
      if (_usbDrivePaths.isNotEmpty) {
        setState(() {});
      }
    });*/
  }

  Future<void> _checkUsb() async {
    _usbDrivePaths = await _getUsbDrivePaths();
    if (_usbDrivePaths.isNotEmpty) {
      setState(() {});
    }
  }

  Future<List<String>> _getUsbDrivePaths() async {
    List<String> ret = [];
    await Process.run("cmd.exe", [
      "/c",
      "wmic logicaldisk where DriveType=2 get DeviceID, VolumeName, ProviderName"
    ]).then((value) {
      //List<String> ret = value.stdout;
      List<String> driveIds = value.stdout.split("\r\n");
      var drives = driveIds
          .where((e) => e.isNotEmpty && !e.contains("DeviceID"))
          .toList();
      for (var item in driveIds) {
        String tmp = item.replaceAll('"', '');
        tmp = tmp.replaceAll(RegExp(r'\s+'), '');
        if (tmp.isNotEmpty && !tmp.contains("DeviceID")) {
          ret.add(tmp);
        }
      }
      print(ret);
    });
    return ret;
  }

  Future<void> extractZipFile(String zipFilePath) async {
    InputFileStream inputStream = InputFileStream(zipFilePath);
    final archive = ZipDecoder().decodeBuffer(inputStream);
    extractArchiveToDisk(archive, './Download');
    inputStream.close();
  }

  Future<String> downloadFile(String url) async {
    const Map<String, String> headers = {
      "user-agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    };
    // Send GET request to API endpoint
    final response = await http.get(Uri.parse(url), headers: headers);
    final filename = './Download/' + url.split('/')[5] + '.zip';
    // Check if the request was successful
    if (response.statusCode == 200) {
      // Parse the JSON response

      final jsonResponse = jsonDecode(utf8.decode(response.bodyBytes));
      // Get the download URL
      final downloadUrl = jsonResponse['assets'][0]['browser_download_url'];

      // Create a new file with the same name as the downloaded file
      final file = File(filename);
      // Open a byte stream to write the downloaded file
      final sink = file.openWrite();
      // Send a GET request to the download URL
      final downloadResponse = await http.get(Uri.parse(downloadUrl));
      // Write the response body to the file
      sink.add(downloadResponse.bodyBytes);
      // Close the stream
      await sink.close();
      await extractZipFile(filename);
      // Handle the downloaded file
    } else {
      // Handle the error
    }
    return filename;
  }

  Future<void> _copyFolderToUsb() async {
    if (_selectedDrivePath == "") {
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('Copy to USB Memory'),
            content: Text('USB Drive is not selected'),
            actions: <Widget>[
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                child: const Text('Close'),
              ),
            ],
          );
        },
      );
      return;
    }
    final folder = Directory('./Download');
    if (folder.existsSync()) {
      folder.deleteSync(recursive: true);
    }
    folder.createSync();
    List<String> urls = [
      "https://api.github.com/repos/THZoria/AtmoPack-Vanilla/releases/latest",
      "https://api.github.com/repos/CTCaer/hekate/releases/latest"
    ];
    for (var url in urls) {
      try {
        final filename = await downloadFile(url);
        final file = File(filename);
        file.deleteSync();
      } catch (e) {
        print("Error: $e");
      }
    }
    setState(() {
      _copyProgress = 0;
    });
    final Directory folderToCopy = Directory('./Download');
    if (!folderToCopy.existsSync()) {
      folderToCopy.createSync();
    }
    final Directory copiedFolder = Directory('$_selectedDrivePath/');
    final List<FileSystemEntity> entityList =
        folderToCopy.listSync(recursive: true, followLinks: false);
    final int entityCount = entityList.length;
    int copiedCount = 0;

    for (FileSystemEntity entity in entityList) {
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
    }

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
