$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "d:\MEGA\บันทึกข้อความ\บันทึกข้อความ\บันทึกข้อความส่งบันทึกหลังแผนการจัดการเรียนรู้ 1-2569.docx"
    $pdfPath = "d:\MEGA\บันทึกข้อความ\บันทึกข้อความ\scratch\preview_post_lesson_memo.pdf"
    $doc = $word.Documents.Open($docPath)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "Word Page Count: $pages"
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close([ref]$false)
    Write-Host "Exported to PDF: $pdfPath"
} catch {
    Write-Error $_
} finally {
    $word.Quit()
}
