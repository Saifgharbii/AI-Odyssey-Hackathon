import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:video_player/video_player.dart';

class MediaProcessingPage extends StatefulWidget {
  const MediaProcessingPage({super.key});

  @override
  State<MediaProcessingPage> createState() => _FakeAIDemoState();
}

class _FakeAIDemoState extends State<MediaProcessingPage> {
  File? _inputImage;
  File? _preparedResponseImage;
  File? _preparedResponseVideo;
  String _preparedResponseText = '';
  bool _isProcessing = false;
  bool _showingResults = false;
  bool _videoError = false;
  VideoPlayerController? _videoController;
  final _promptController = TextEditingController();

  // Secret gesture detector counter
  int _secretTapCount = 0;
  final int _requiredTaps = 5;

  Future<void> _pickInputImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);

    if (image != null) {
      setState(() {
        _inputImage = File(image.path);
        _showingResults = false;
      });
    }
  }

  Future<void> _prepareResponseImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);

    if (image != null) {
      setState(() {
        _preparedResponseImage = File(image.path);
      });
    }
  }

  Future<void> _prepareResponseVideo() async {
    final ImagePicker picker = ImagePicker();
    final XFile? video = await picker.pickVideo(source: ImageSource.gallery);

    if (video != null) {
      setState(() {
        _preparedResponseVideo = File(video.path);
        _videoError = false;
      });

      try {
        await _initializeVideo(video.path);
      } catch (e) {
        setState(() {
          _videoError = true;
          _preparedResponseVideo = null;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('This video format is not supported. Please try another video.')),
        );
      }
    }
  }

  Future<void> _initializeVideo(String path) async {
    final controller = VideoPlayerController.file(File(path));
    try {
      await controller.initialize();
      setState(() {
        _videoController?.dispose();
        _videoController = controller;
      });
    } catch (e) {
      controller.dispose();
      throw e;
    }
  }

  void _processWithFakeDelay() async {
    if (_inputImage == null || _preparedResponseImage == null ||
        _preparedResponseVideo == null || _promptController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please set up all responses first')),
      );
      return;
    }

    setState(() {
      _isProcessing = true;
      _showingResults = false;
    });

    // Fake processing delay
    await Future.delayed(const Duration(seconds: 8));

    setState(() {
      _isProcessing = false;
      _showingResults = true;
    });
  }

  void _handleSecretTap() {
    setState(() {
      _secretTapCount++;
      if (_secretTapCount >= _requiredTaps) {
        _showSecretDialog();
        _secretTapCount = 0;
      }
    });
  }

  void _showSecretDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Secret Setup'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton(
              onPressed: _prepareResponseImage,
              child: const Text('Select Response Image'),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: _prepareResponseVideo,
              child: const Text('Select Response Video'),
            ),
            const SizedBox(height: 8),
            TextField(
              onChanged: (value) => setState(() => _preparedResponseText = value),
              decoration: const InputDecoration(
                labelText: 'Set Response Text',
              ),
              maxLines: 3,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _videoController?.dispose();
    _promptController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Image Enhancer'),
        backgroundColor: theme.primaryColor,
      ),
      body: GestureDetector(
        onTapDown: (details) {
          // Only detect taps in top-right corner
          print(details.globalPosition);
          if (details.globalPosition.dx > MediaQuery.of(context).size.width - 50 &&
              details.globalPosition.dy < 120) {
            _handleSecretTap();
          }
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ElevatedButton(
                onPressed: _pickInputImage,
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.primaryColor,
                ),
                child: const Text('Select Image to Enhance'),
              ),
              if (_inputImage != null) ...[
                const SizedBox(height: 16),
                Image.file(
                  _inputImage!,
                  height: 200,
                  fit: BoxFit.cover,
                ),
              ],
              if (!_isProcessing) ...[
                const SizedBox(height: 16),
                TextField(
                  controller: _promptController,
                  decoration: const InputDecoration(
                    labelText: 'Enter description for enhancement',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                ),
              ],
              const SizedBox(height: 16),
              SizedBox(
                height: 50,
                child: ElevatedButton(
                  onPressed: _isProcessing ? null : _processWithFakeDelay,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: theme.primaryColor,
                  ),
                  child: _isProcessing
                      ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 3,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                      : const Text('Enhance Image'),
                ),
              ),
              if (_showingResults) ...[
                const SizedBox(height: 24),
                const Text('Enhanced Results:',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)
                ),
                const SizedBox(height: 16),
                if (_preparedResponseText.isNotEmpty)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(_preparedResponseText),
                    ),
                  ),
                if (_preparedResponseImage != null) ...[
                  const SizedBox(height: 16),
                  Image.file(_preparedResponseImage!),
                ],
                if (_preparedResponseVideo != null &&
                    _videoController != null &&
                    _videoController!.value.isInitialized &&
                    !_videoError) ...[
                  const SizedBox(height: 16),
                  AspectRatio(
                    aspectRatio: _videoController!.value.aspectRatio,
                    child: VideoPlayer(_videoController!),
                  ),
                  IconButton(
                    icon: Icon(
                      _videoController!.value.isPlaying ? Icons.pause : Icons.play_arrow,
                    ),
                    onPressed: () {
                      setState(() {
                        _videoController!.value.isPlaying
                            ? _videoController!.pause()
                            : _videoController!.play();
                      });
                    },
                  ),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }
}


/*import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:dio/dio.dart';
import 'package:video_player/video_player.dart';

class MediaProcessingPage extends StatefulWidget {
  const MediaProcessingPage({super.key});

  @override
  State<MediaProcessingPage> createState() => _MediaProcessingPageState();
}

class _MediaProcessingPageState extends State<MediaProcessingPage> {
  File? _selectedImage;
  final _promptController = TextEditingController();
  bool _isLoading = false;
  String? _responseText;
  String? _responseImageUrl;
  String? _responseVideoUrl;
  VideoPlayerController? _videoController;

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);

    if (image != null) {
      setState(() {
        _selectedImage = File(image.path);
      });
    }
  }

  Future<void> _processMedia() async {
    if (_selectedImage == null || _promptController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image and enter a prompt')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _responseText = null;
      _responseImageUrl = null;
      _responseVideoUrl = null;
    });

    try {
      // Example API call - replace with your actual server endpoint
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(_selectedImage!.path),
        'prompt': _promptController.text,
      });

      final response = await Dio().post(
        "http://backend-server.loca.lt/process",
        data: formData,
      );

      print(response.data);

      setState(() {
        _responseText = response.data['text'];
        _responseImageUrl = response.data['image_url'];
        _responseVideoUrl = response.data['video_url'];

        if (_responseVideoUrl != null) {
          _videoController = VideoPlayerController.network(_responseVideoUrl!)
            ..initialize().then((_) {
              setState(() {});
            });
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _downloadFile(String url, String type) async {
    try {
      final directory = await getExternalStorageDirectory();
      if (directory == null) throw Exception('Cannot access storage');

      final fileName = '${DateTime.now().millisecondsSinceEpoch}_$type';
      final filePath = '${directory.path}/$fileName';

      await Dio().download(url, filePath);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$type downloaded successfully')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error downloading $type: ${e.toString()}')),
      );
    }
  }

  @override
  void dispose() {
    _promptController.dispose();
    _videoController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Media Processing'),
        backgroundColor: theme.primaryColor,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              onPressed: _pickImage,
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.primaryColor,
                foregroundColor: theme.colorScheme.onPrimary,
              ),
              child: const Text('Select Image'),
            ),
            if (_selectedImage != null) ...[
              const SizedBox(height: 16),
              Image.file(
                _selectedImage!,
                height: 200,
                fit: BoxFit.cover,
              ),
            ],
            const SizedBox(height: 16),
            TextField(
              controller: _promptController,
              decoration: InputDecoration(
                labelText: 'Enter your prompt',
                border: const OutlineInputBorder(),
                filled: true,
                fillColor: theme.colorScheme.surface,
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _processMedia,
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.primaryColor,
                foregroundColor: theme.colorScheme.onPrimary,
              ),
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Process'),
            ),
            if (_responseText != null) ...[
              const SizedBox(height: 24),
              Card(
                color: theme.colorScheme.surface,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Response Text:',
                        style: theme.textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(_responseText!),
                      IconButton(
                        icon: const Icon(Icons.download),
                        onPressed: () => _downloadFile(_responseText!, 'text'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            if (_responseImageUrl != null) ...[
              const SizedBox(height: 16),
              Card(
                color: theme.colorScheme.surface,
                child: Column(
                  children: [
                    Image.network(_responseImageUrl!),
                    IconButton(
                      icon: const Icon(Icons.download),
                      onPressed: () => _downloadFile(_responseImageUrl!, 'image'),
                    ),
                  ],
                ),
              ),
            ],
            if (_responseVideoUrl != null && _videoController != null) ...[
              const SizedBox(height: 16),
              Card(
                color: theme.colorScheme.surface,
                child: Column(
                  children: [
                    AspectRatio(
                      aspectRatio: _videoController!.value.aspectRatio,
                      child: VideoPlayer(_videoController!),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        IconButton(
                          icon: Icon(
                            _videoController!.value.isPlaying
                                ? Icons.pause
                                : Icons.play_arrow,
                          ),
                          onPressed: () {
                            setState(() {
                              _videoController!.value.isPlaying
                                  ? _videoController!.pause()
                                  : _videoController!.play();
                            });
                          },
                        ),
                        IconButton(
                          icon: const Icon(Icons.download),
                          onPressed: () => _downloadFile(_responseVideoUrl!, 'video'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}*/