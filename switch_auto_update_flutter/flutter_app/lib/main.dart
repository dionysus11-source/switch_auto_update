import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:archive/archive_io.dart';
import 'package:switch_auto_updater/widgets/button.dart';
import 'package:desktop_window/desktop_window.dart';

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
          primarySwatch: Colors.grey),
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
  bool isDownloading = false;

  @override
  void initState() {
    super.initState();
    DesktopWindow.setWindowSize(const Size(600, 800));
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
      for (var item in driveIds) {
        String tmp = item.replaceAll('"', '');
        tmp = tmp.replaceAll(RegExp(r'\s+'), '');
        if (tmp.isNotEmpty && !tmp.contains("DeviceID")) {
          ret.add(tmp);
        }
      }
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
    final filename = './Download/${url.split('/')[5]}.zip';
    // Check if the request was successful
    if (response.statusCode == 200) {
      // Parse the JSON response
      setState(() {
        isDownloading = true;
      });

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
      setState(() {
        isDownloading = false;
      });
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
            title: const Text('Copy to USB Memory'),
            content: const Text('USB Drive is not selected'),
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
    setState(() {
      _copyProgress = 0.01;
    });
    final folder = Directory('./Download');
    if (folder.existsSync()) {
      folder.deleteSync(recursive: true);
    }
    folder.createSync();
    List<String> urls = [
      "https://codeberg.org/api/v1/repos/Zoria/AtmoPack-Vanilla/releases/latest",
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
      backgroundColor: const Color(0xFF181818),
      body: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(
              height: 20,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text(
                      "Hey, Switch Users",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 28,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      "Welcome back",
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 18,
                      ),
                    ),
                  ],
                )
              ],
            ),
            const SizedBox(
              height: 20,
            ),
            Text(
              'Selected USB $_selectedDrivePath',
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 22,
              ),
            ),
            const SizedBox(
              height: 30,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                InkWell(
                  onTap: _checkUsb,
                  child: const MyButton(
                    text: "Refresh",
                    bgColor: Color(0xFFF1B33B),
                    textColor: Colors.black,
                  ),
                ),
                InkWell(
                  onTap: _copyFolderToUsb,
                  child: const MyButton(
                    text: "Copy",
                    bgColor: Color(0xFF1F2123),
                    textColor: Colors.white,
                  ),
                ),
              ],
            ),
            const SizedBox(
              height: 20,
            ),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Drives',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 36,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  'View All',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 18,
                  ),
                ),
              ],
            ),
            const SizedBox(
              height: 20,
            ),
            SizedBox(
              height: 200,
              child: ListView.builder(
                itemCount: _usbDrivePaths.length,
                itemBuilder: (context, index) {
                  return InkWell(
                    onTap: () {
                      setState(() {
                        _selectedDrivePath = _usbDrivePaths[index];
                      });
                    },
                    child: Container(
                        clipBehavior: Clip.hardEdge,
                        decoration: BoxDecoration(
                            color: const Color(0xFF1F2123),
                            borderRadius: BorderRadius.circular(20)),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(
                            vertical: 30,
                            horizontal: 30,
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              Text(
                                _usbDrivePaths[index],
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 32,
                                  fontWeight: FontWeight.w200,
                                ),
                              ),
                              Transform.scale(
                                scale: 2.2,
                                child: Transform.translate(
                                  offset: const Offset(-5, 12),
                                  child: const Icon(
                                    Icons.usb_rounded,
                                    color: Colors.white,
                                    size: 88,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        )),
                  );
                },
              ),
            ),
            if (_usbDrivePaths == null)
              const CircularProgressIndicator()
            else
              Row(
                children: [
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (!isDownloading)
                          CircularProgressIndicator(
                            value: _copyProgress,
                          )
                        else
                          const CircularProgressIndicator(),
                        const SizedBox(
                          height: 20,
                        ),
                        if (_copyProgress == 1)
                          const Text('Copy complete! Remove Usb memory',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 30,
                              )),
                        if (_copyProgress == 0.01)
                          const Text(
                            'Downloading...',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 30,
                            ),
                          )
                        else if (_copyProgress > 0.01 && _copyProgress < 1)
                          const Text(
                            'Copy In Progress...',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 30,
                            ),
                          )
                      ],
                    ),
                  ),
                ],
              ),
            const SizedBox(
              height: 5,
            ),
          ],
        ),
      ),
    );
  }
}
