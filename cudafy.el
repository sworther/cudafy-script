(defun cudafy/for2if()
  "example of calling a external command.
passing text of region to its stdin.
replace region by its stdout."
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-stdin.py for2if"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)))

(defun cudafy/kji-irregular()
  "example of calling a external command.
passing text of region to its stdin.
replace region by its stdout."
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-stdin.py  kji_irregular"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)))


(defun cudafy/kji-general-offset()
  "example of calling a external command.
passing text of region to its stdin.
replace region by its stdout."
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-stdin.py kji_general_offset"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)))

(defun cudafy/find-global-variable()
  "find the global variable used in the kernel,
put them in the kernel parameter list"
  (interactive)
  (let (
        (cmd (format "./auxiliary/cudafy-stdin.py find_variable"))
        (cuda-lvalue nil)
        (cudafy-var nil))
    (shell-command-on-region (region-beginning) (region-end) cmd "*cudafy*" nil nil t)
    (with-current-buffer "*cudafy*"
      (goto-char (point-min))

      (setq cuda-lvalue
            (buffer-substring-no-properties
             (line-beginning-position)
             (line-end-position)))

      (next-line)

      (setq cudafy-var
            (buffer-substring-no-properties
             (line-beginning-position)
             (line-end-position)))
      )

    (kill-new  cudafy-var)
    (kill-new cuda-lvalue)

    ;; (switch-to-buffer-other-window "*cudafy*")
    (view-buffer-other-window "*cudafy*")
    (other-window 1)

    (goto-char (region-beginning))
    (search-backward ")")
    (if (y-or-n-p "add global variable in the function?")
        (insert cudafy-var)
      nil)
    (delete-other-windows)
    ))


(defun cudafy/find-cpu-arrs()
  "find the global array used in the kernel and put them in the kernel parameter list"
  (interactive)
  (let (
        (cmd (format "./auxiliary/cudafy-c2g-stdin.py find_arrs_in_func"))
        (cudafy-array nil))
    (shell-command-on-region (region-beginning) (region-end) cmd "*cudafy*" nil nil t)
    (with-current-buffer "*cudafy*"
      (goto-char (point-min))
      (setq cudafy-array
            (buffer-string))
      )
    (kill-new  cudafy-array)
    ))


    (defun cudafy/find-array()
      "find the global array used in the kernel and put them in the kernel parameter list"
      (interactive)
      (let (
            (cmd (format "./auxiliary/cudafy-stdin.py find_array"))
            (cudafy-array nil))
        (shell-command-on-region (region-beginning) (region-end) cmd "*cudafy*" nil nil t)
        (with-current-buffer "*cudafy*"
          (goto-char (point-min))
          (setq cudafy-array
                (buffer-string))
          )
        (kill-new  cudafy-array)

    ;; (switch-to-buffer-other-window "*cudafy*")
    (view-buffer-other-window "*cudafy*")
    (other-window 1)

    (goto-char (region-beginning))
    (search-backward ")")
    (if (y-or-n-p "add global array in the function?")
        (yank)
      nil)
    (delete-other-windows)
    ))


(defun cudafy/constuct-kernel()
  "add kernel name and width, height, depth to a for loop"
  (interactive)
  (let ((cuda-thread-index-string
         "    int width = blockIdx.x * blockDim.x + threadIdx.x;
    int height = blockIdx.y * blockDim.y + threadIdx.y;
    int depth = blockIdx.z * blockDim.z + threadIdx.z;\n")
        (start (min (region-beginning) (region-end)))
        (end   (max (region-beginning) (region-end)))
        (fn-name nil))

    (setq fn-name (read-from-minibuffer "input the kernel name: "))
    (goto-char end)
    (insert "}\n")
    (goto-char start)
    (insert (format "__global__ void cuda_%s()\n{\n" fn-name))
    (insert cuda-thread-index-string)
    ))


(defun cudafy/3D-wrapper()
  "construct cuda 3D kernel"
  (interactive)
  (let (
        (cmd (format "./auxiliary/cudafy-stdin.py make_3D_wrapper"))
        (dim-block nil)
        (cudafy-wrapper nil))
    (shell-command-on-region (point-min) (point-max) cmd "*cudafy*" nil nil t)

    ;; copy the *cudafy* buffer
    (with-current-buffer "*cudafy*"
      (goto-char (point-min))
      (setq cudafy-wrapper
            (buffer-string))
      )

    (setq dim-block "  dim3 dimBlock(32, 4, 2);
  dim3 dimGrid((nx + 2 + 31)/32,  (ny + 2 + 3)/4, (nz + 2 + 1)/2);\n\n")


    ;; (switch-to-buffer-other-window "*cudafy*")
    (view-buffer-other-window "*cudafy*")
    (other-window 1)

    (if (y-or-n-p "add 3D dimBlock variable?")
        (insert dim-block)
      nil)


    (if (y-or-n-p "add wrapper function?")
        (insert cudafy-wrapper)
      nil)

    (delete-other-windows)
    ))

(defun cudafy/change-to-2D-arg ()
  "insert 2D kernel block thread kernels argument"
  (interactive)
  (let ((type (read-from-minibuffer "input 2D kernel type: 1(xy)  2(xz) 3(yz) :"))
        (id1 nil)
        (id2 nil)
        (dim-block nil))

    (if (string= type "1")
        (progn
          (setq id1 "nx")
          (setq id2 "ny")))

    (if (string= type "2")
        (progn
          (setq id1 "nx")
          (setq id2 "nz")))

    (if (string= type "3")
        (progn
          (setq id1 "ny")
          (setq id2 "nz")))

  (setq dim-block
        (format "  dim3 dimBlock2_%s(32, 4, 1);
  dim3 dimGrid2_%s(( %s + 2 + 31)/32,  (%s + 2 + 3)/4, 1);\n" type type id1 id2))

  (insert dim-block)

  (re-search-forward "dimBlock" (line-end-position))
  (replace-match (format "dimBlock2_%s" type))
  (beginning-of-line)

  (re-search-forward "dimGrid" (line-end-position))
  (replace-match (format "dimGrid2_%s" type))
  (beginning-of-line)

))


(defun cudafy/alloc()
  "alloc device memory for arrs"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py alloc"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)))


(defun cudafy/dealloc()
  "dealloc device memory"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py dealloc"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)))

(defun cudafy/upload()
  "upload arrs from cpu to gpu"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py upload"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)))

(defun cudafy/upload_func()
  "upload arrs in a function from cpu to gpu"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py upload_func"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd "*cudafy*" nil nil t)
    (with-current-buffer "*cudafy*"
      (kill-new (buffer-string)))
    ))


(defun cudafy/download()
  "download arrs in a function from gpu to cpu"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py download"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)
    (with-current-buffer "*cudafy*"
      (kill-new (buffer-string)))
    ))

(defun cudafy/download_func()
  "download arrs in a function from gpu to cpu"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py download_func"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd "*cudafy*" nil nil t)))


(defun cudafy/function_transform()
  "function name transform"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-stdin.py func_name_transform"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd nil "REPLACE" nil t)
    (with-current-buffer "*cudafy*"
      (kill-new (buffer-string)))
    ))

(defun cudafy/register_cpu_arrs()
  "function name transform"
  (interactive)
  (let ((cmd
         (format
          "./auxiliary/cudafy-c2g-stdin.py register_cpu_arrs"
          )))
    (shell-command-on-region (region-beginning) (region-end) cmd "*cudafy*" nil nil t)
    (with-current-buffer "*cudafy*"
      (kill-new (buffer-string)))
    ))


(spacemacs/set-leader-keys
  "oa"  'cudafy/find-array
  "oA"  'cudafy/find-cpu-arrs
  "ov"  'cudafy/find-global-variable
  "of"  'cudafy/for2if
  "oF"  'cudafy/function_transform
  "og"  'cudafy/kji-general-offset
  "oc"  'cudafy/constuct-kernel
  "ow"  'cudafy/3D-wrapper
  "oi"  'cudafy/change-to-2D-arg
  "or"  'cudafy/kji-irregular
  "our" 'cudafy/register_cpu_arrs
  "ouU" 'cudafy/upload
  "ouu" 'cudafy/upload_func
  "ouD" 'cudafy/download
  "oud" 'cudafy/download_func
  "oua" 'cudafy/alloc
  "ouc" 'cudafy/dealloc
  )
