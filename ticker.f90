module ticker

    implicit none

    integer :: lun
    logical :: template_exists
    logical :: initialized = .false.


    integer, parameter :: NTICKS_MAX=1048576
    integer, parameter :: THIN_OUTPUT=100
    real, dimension(1:NTICKS_MAX) :: tick_time
    integer :: nticks
    integer :: curtick = 0
    real :: max_tick_time

    character(len=*), parameter :: progress = "/root/shared/results/progress"
    character(len=*), parameter :: progress_template = "/root/shared/progress_template"

contains


    subroutine ticker_init()
        integer stat
        if (.not. initialized) then
            inquire(file=progress_template, exist=template_exists)
            if (template_exists) then
                open(newunit=lun, file=progress_template, action="read", iostat=stat)
                do nticks=1,NTICKS_MAX
                    read (lun,*,iostat=stat) tick_time(nticks)
                    if (stat /= 0) exit
                end do
                max_tick_time = tick_time(nticks-1)
                close(lun)
                open(newunit=lun,file=progress,action="write", iostat=stat)

            else
                open(newunit=lun, file=progress_template, action="write")
            end if
            initialized=.true.
        end if
    end subroutine


    subroutine tick()
        real atime

        if (.not. initialized) call ticker_init

        if (template_exists) then

            !$omp atomic
            curtick = curtick + 1

            if (mod(curtick,THIN_OUTPUT)==0) then
                if (curtick < nticks) then
                    write (lun,*) tick_time(curtick)/max_tick_time
                else
                    write (lun,*) 1.
                end if
                flush(lun)
            endif
        else
            call cpu_time(atime)
            write (lun,*) atime
        end if 
    end subroutine


end module
