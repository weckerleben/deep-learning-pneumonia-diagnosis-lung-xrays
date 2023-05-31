package com.neumoscan.app

import androidx.compose.foundation.layout.Box
import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.icu.text.SimpleDateFormat
import android.net.Uri
import android.os.Bundle
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import android.os.Environment
import android.provider.MediaStore
import android.widget.ImageView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.neumoscan.app.ui.theme.NeumoScanTheme
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.Date
import java.util.Locale


class MainActivity : ComponentActivity() {
    private companion object {
        private const val REQUEST_IMAGE_CAPTURE = 1
        private const val PERMISSION_REQUEST_CODE = 1001
    }

    private var currentPhotoPath: String? = null
    private lateinit var imageView: ImageView


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NeumoScanTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            verticalArrangement = Arrangement.Center,
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Greeting("Android")
                            Spacer(modifier = Modifier.height(16.dp))
                            TakePhotoButton(this@MainActivity)
                        }
                        if (currentPhotoPath != null) {
                            ShowPhoto(currentPhotoPath!!)
                        }
                    }
                }
            }
        }
        checkAndRequestPermissions()
    }

    private fun checkAndRequestPermissions() {
        val permissionsToRequest = mutableListOf<String>()
        val cameraPermission = Manifest.permission.CAMERA
        val storagePermission = Manifest.permission.WRITE_EXTERNAL_STORAGE

        // Verifica el permiso de la cámara
        if (!isPermissionGranted(cameraPermission)) {
            permissionsToRequest.add(cameraPermission)
        }

        // Verifica el permiso de almacenamiento
        if (!isPermissionGranted(storagePermission)) {
            permissionsToRequest.add(storagePermission)
        }

        // Solicita los permisos necesarios
        if (permissionsToRequest.isNotEmpty()) {
            requestPermissions(permissionsToRequest.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        } else {
            // Todos los permisos ya están otorgados, puedes proceder con la captura de la imagen
        }
    }


    private fun isPermissionGranted(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        if (requestCode == PERMISSION_REQUEST_CODE) {
            var allPermissionsGranted = true
            for (result in grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allPermissionsGranted = false
                    break
                }
            }
            if (allPermissionsGranted) {
                // Los permisos fueron otorgados, puedes proceder con la captura de la imagen
                captureImage()
            } else {
                // Al menos uno de los permisos no fue otorgado, puedes mostrar un mensaje de error o tomar alguna otra acción
                Toast.makeText(this, "Se requieren permisos de cámara", Toast.LENGTH_SHORT).show()
            }
        } else {
            super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        }
    }

    private fun captureImage() {
        val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        if (takePictureIntent.resolveActivity(packageManager) != null) {
            val photoFile: File? = try {
                createImageFile()
            } catch (ex: IOException) {
                // Maneja el error al crear el archivo
                ex.printStackTrace()
                null
            }
            // Continúa solo si el archivo se ha creado correctamente
            photoFile?.also {
                val photoURI: Uri = FileProvider.getUriForFile(
                    this,
                    "com.neumoscan.app.fileprovider",
                    it
                )
                // Guarda la ruta de la imagen para su posterior uso
                currentPhotoPath = photoFile.absolutePath
                // Configura la URI del archivo como extra en el intent de la cámara
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == Activity.RESULT_OK) {
            val photoFile = File(currentPhotoPath)
            if (photoFile.exists()) {
                setContent {
                    ShowPhoto(photoFile.absolutePath)
                }
            }
        }
    }

    private fun saveImageToGallery(imageBitmap: Bitmap) {
        val timeStamp: String =
            SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val imageFileName = "JPEG_${timeStamp}.jpg"
        val storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)

        val imageFile = File(storageDir, imageFileName)
        val outputStream = FileOutputStream(imageFile)
        imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream)
        outputStream.flush()
        outputStream.close()

        // Añade la foto a la galería
        val mediaScanIntent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
        val contentUri = Uri.fromFile(imageFile)
        mediaScanIntent.data = contentUri
        sendBroadcast(mediaScanIntent)
    }


    @Composable
    fun Greeting(name: String) {
        Text(
            text = "Hello $name!",
            modifier = Modifier.padding(16.dp),
            color = Color.White,
            fontWeight = FontWeight.Bold
        )
    }

    @Throws(IOException::class)
    private fun createImageFile(): File {
        // Crea un nombre único para el archivo de imagen
        val timeStamp: String =
            SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile(
            "JPEG_${timeStamp}_", /* prefijo del archivo */
            ".jpg", /* extensión del archivo */
            storageDir /* directorio de almacenamiento */
        ).apply {
            // Guarda la ruta del archivo
            currentPhotoPath = absolutePath
        }
    }

    private fun dispatchTakePictureIntent() {
        captureImage()
    }

    @Composable
    fun TakePhotoButton(activity: ComponentActivity) {
        Button(
            onClick = { dispatchTakePictureIntent() },
            modifier = Modifier.padding(16.dp)
        ) {
            Text(text = "Take Photo")
        }
    }

    @Preview(showBackground = true)
    @Composable
    fun DefaultPreview() {
        NeumoScanTheme {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Greeting("Android")
                Spacer(modifier = Modifier.height(16.dp))
                TakePhotoButton(activity = ComponentActivity())
            }
        }
    }

    @Composable
    fun ShowPhoto(photoPath: String) {
        val imageBitmap = loadImageBitmap(photoPath)
        imageBitmap?.let {
            Image(
                painter = BitmapPainter(it),
                contentDescription = null,
                modifier = Modifier.padding(16.dp)
            )
        }
    }

    private fun loadImageBitmap(photoPath: String): ImageBitmap? {
        val photoFile = File(photoPath)
        return if (photoFile.exists()) {
            BitmapFactory.decodeFile(photoFile.absolutePath)?.asImageBitmap()
        } else {
            null
        }
    }
}