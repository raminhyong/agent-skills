
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("H:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\บันทึกข้อความไปราชการ17สค69.docx")
$doc.SaveAs("H:\My Drive\งานหัวหน้ากลุ่มสาระฯ รามิล 2569\บันทึกข้อความ\scratch\preview17.pdf", 17)
$doc.Close()
$word.Quit()
